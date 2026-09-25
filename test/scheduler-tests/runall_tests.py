#!/usr/bin/env python3

import argparse
import unittest
import tests.config as config

def main():
    parser = argparse.ArgumentParser(
        description="mpifileutils tests"
    )
    parser.add_argument("--bin-dir", type=str, default="")
    parser.add_argument("--scheduler", type=str, choices=["slurm", "flux", "none"], default="none")
    parser.add_argument("-N", "--nodes", type=int, default=None, help="Required when --scheduler [slurm/flux] is selected")
    parser.add_argument("-n", "--tasks", type=int, default=None, help="Required when --scheduler [slurm/flux] is selected")
    parser.add_argument("-np", "--processes", type=int, default=None, help="Required when --scheduler none is selected")
    parser.add_argument("--tmp-dir", type=str, default="")
    args = parser.parse_args()
    
    check_missing_scheduler_args(args, parser)
    set_configs(args)

    result = run_tests()
    if result.wasSuccessful():
        print("All tests passed.")
        return 0
    print(f"Tests failed. Failures: {len(result.failures)}, Errors: {len(result.errors)}")
    return 1

def check_missing_scheduler_args(args, parser):
    missing_args = []
    if args.scheduler in ["slurm", "flux"]:
        if not args.nodes:
            missing_args.append("--nodes")
        if not args.tasks:
            missing_args.append("--tasks")
    if args.scheduler == "none":
        if not args.processes:
            missing_args.append("--processes")

    if missing_args:
        parser.error(
            f"{', '.join(missing_args)} is required when --scheduler {args.scheduler} is selected"
        ) 

def set_configs(args):
    config.bin_dir = args.bin_dir
    config.scheduler = args.scheduler
    if config.scheduler == "slurm":
        config.run_cmd = ["srun", "-N", str(args.nodes), "-n", str(args.tasks)]
    if config.scheduler == "flux":
        config.run_cmd = ["flux", "run", f"--nodes={args.nodes}", f"--ntasks={args.tasks}"]
    if config.scheduler == "none":
        config.run_cmd = ["mpirun", "-np", str(args.processes)]
    config.tmp_dir = args.tmp_dir

def run_tests():
    suite = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
    return unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    raise SystemExit(main())
