#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def genome_from_filename(path, suffix):
    name = os.path.basename(path)
    if not name.endswith(suffix):
        raise ValueError("unexpected anvi'o output name: " + name)
    return name[: -len(suffix)]


def concatenate(inputs, output, suffix):
    fieldnames = None
    rows = []
    for path in sorted(inputs):
        genome_id = genome_from_filename(path, suffix)
        current = read_tsv(path)
        if not current:
            raise ValueError("empty anvi'o table: " + path)
        current_fields = list(current[0])
        if fieldnames is None:
            fieldnames = current_fields
        elif current_fields != fieldnames:
            raise ValueError("inconsistent anvi'o headers: " + path)
        for row in current:
            row = dict(row)
            row["genome_id"] = genome_id
            rows.append(row)
    output_fields = ["genome_id"] + [x for x in (fieldnames or []) if x != "genome_id"]
    with open(output, "w", newline="") as handle:
        writer = csv.DictWriter(handle, output_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def locate_modules_db(kegg_data_dir):
    candidates = []
    for root, _, files in os.walk(kegg_data_dir):
        if "MODULES.db" in files:
            candidates.append(os.path.join(root, "MODULES.db"))
    if len(candidates) != 1:
        raise ValueError("expected exactly one MODULES.db, found {}".format(len(candidates)))
    return candidates[0]


def modules_db_content_hash(path):
    with sqlite3.connect(path) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "self" in tables:
            rows = list(db.execute("SELECT key, value FROM self ORDER BY key"))
            for key, value in rows:
                if "hash" in str(key).lower():
                    return str(value)
    return "NA"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--representatives", required=True)
    parser.add_argument("--modules", nargs="+", required=True)
    parser.add_argument("--module-paths", nargs="+", required=True)
    parser.add_argument("--module-steps", nargs="+", required=True)
    parser.add_argument("--hits", nargs="+", required=True)
    parser.add_argument("--contigs-dbs", nargs="+", required=True)
    parser.add_argument("--kegg-data-dir", required=True)
    parser.add_argument("--strict-threshold", type=float, required=True)
    parser.add_argument("--sensitivity-threshold", type=float, required=True)
    parser.add_argument("--modules-output", required=True)
    parser.add_argument("--missing-output", required=True)
    parser.add_argument("--paths-output", required=True)
    parser.add_argument("--steps-output", required=True)
    parser.add_argument("--hits-output", required=True)
    parser.add_argument("--database-manifest", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    representatives = read_tsv(args.representatives)
    expected = {row["genome_id"] for row in representatives}
    groups = [
        (args.modules, "_modules.txt"),
        (args.module_paths, "_module_paths.txt"),
        (args.module_steps, "_module_steps.txt"),
        (args.hits, "_hits.txt"),
        (args.contigs_dbs, "-CONTIGS.db"),
    ]
    for paths, suffix in groups:
        observed = {genome_from_filename(path, suffix) for path in paths}
        if observed != expected:
            raise ValueError("anvi'o genome accounting mismatch for {}: missing={} extra={}".format(
                suffix, sorted(expected - observed), sorted(observed - expected)))

    path_rows = concatenate(args.module_paths, args.paths_output, "_module_paths.txt")
    step_rows = concatenate(args.module_steps, args.steps_output, "_module_steps.txt")
    hit_rows = concatenate(args.hits, args.hits_output, "_hits.txt")

    normalized = []
    missing_rows = []
    required = {"module", "module_name", "stepwise_module_completeness", "pathwise_module_completeness"}
    for path in sorted(args.modules):
        genome_id = genome_from_filename(path, "_modules.txt")
        rows = read_tsv(path)
        if not rows or not required.issubset(rows[0]):
            raise ValueError("missing required anvi'o module columns: " + path)
        for row in rows:
            stepwise = float(row["stepwise_module_completeness"])
            pathwise = float(row["pathwise_module_completeness"])
            if not (0 <= stepwise <= 1 and 0 <= pathwise <= 1):
                raise ValueError("module completeness outside [0,1]: " + path)
            warning = row.get("warnings", "")
            if warning and "not assess" in warning.lower():
                state = "not_assessable"
            elif pathwise >= args.strict_threshold:
                state = "complete"
            elif pathwise >= args.sensitivity_threshold:
                state = "near_complete"
            elif pathwise > 0:
                state = "incomplete"
            else:
                state = "not_detected"
            normalized.append({
                "genome_id": genome_id,
                "module_id": row["module"],
                "module_name": row["module_name"],
                "module_definition": row.get("module_definition", "NA"),
                "state": state,
                "pathwise_completeness": "{:.6f}".format(pathwise),
                "stepwise_completeness": "{:.6f}".format(stepwise),
                "strict_complete": str(pathwise >= args.strict_threshold).lower(),
                "sensitivity_complete_75": str(pathwise >= args.sensitivity_threshold).lower(),
                "enzyme_hits": row.get("enzyme_hits_in_module", "NA"),
                "gene_caller_ids": row.get("gene_caller_ids_in_module", "NA"),
                "warnings": warning or "NA",
            })

    step_keys = set(step_rows[0]) if step_rows else set()
    step_column = next((x for x in ("step", "module_step", "step_definition") if x in step_keys), None)
    complete_column = next((x for x in ("step_is_complete", "stepwise_step_is_complete", "complete") if x in step_keys), None)
    for row in step_rows:
        if complete_column and str(row.get(complete_column, "")).lower() in {"false", "0", "no"}:
            missing_rows.append({
                "genome_id": row["genome_id"],
                "module_id": row.get("module", "NA"),
                "missing_step": row.get(step_column, "NA") if step_column else "NA",
                "source": "anvi-estimate-metabolism",
            })

    fields = ["genome_id", "module_id", "module_name", "module_definition", "state",
              "pathwise_completeness", "stepwise_completeness", "strict_complete",
              "sensitivity_complete_75", "enzyme_hits", "gene_caller_ids", "warnings"]
    with open(args.modules_output, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(normalized)
    with open(args.missing_output, "w", newline="") as handle:
        fields = ["genome_id", "module_id", "missing_step", "source"]
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(missing_rows)

    modules_db = locate_modules_db(args.kegg_data_dir)
    db_hash = sha256(modules_db)
    content_hash = modules_db_content_hash(modules_db)
    with open(args.database_manifest, "w") as handle:
        handle.write("database\tpath\tsha256\tcontent_hash\n")
        handle.write("anvio_MODULES.db\t{}\t{}\t{}\n".format(modules_db, db_hash, content_hash))

    checkpoint = {
        "checkpoint": "C08",
        "status": "pass",
        "run_id": args.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": "ANVIO_ESTIMATE_METABOLISM",
        "input_sha256": sha256(args.representatives),
        "database_versions": {"modules_db_sha256": db_hash, "modules_db_content_hash": content_hash},
        "parameters": {"primary_complete_threshold": args.strict_threshold,
                       "sensitivity_threshold": args.sensitivity_threshold,
                       "strategies": ["pathwise", "stepwise"]},
        "metrics": {"genomes": len(expected), "module_calls": len(normalized),
                    "complete_calls": sum(row["state"] == "complete" for row in normalized),
                    "near_complete_calls": sum(row["state"] == "near_complete" for row in normalized),
                    "module_path_rows": len(path_rows), "module_step_rows": len(step_rows),
                    "kofam_hit_rows": len(hit_rows), "missing_step_rows": len(missing_rows)},
    }
    with open(args.checkpoint, "w") as handle:
        json.dump(checkpoint, handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
