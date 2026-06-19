import json
import os
import time

from mcp.server.fastmcp import FastMCP

def run_suite(suite_path: str, options: dict | None = None) -> dict:
    """Execute a Robot Framework test suite and return results."""
    suite_path = str(suite_path)
    from pathlib import Path as P

    rp = P(suite_path)
    if not rp.is_file():
        return {"success": False, "error": f"File not found: {suite_path}"}

    robot_cli: str
    try:
        import robot

        # Use the Python API directly for more control
        robot_cli = "python"
    except ImportError:
        return {"success": False, "error": "Robot Framework is not installed. Run: pip install robotframework"}

    opts = options or {}
    output_dir = opts.get("output_dir", str(rp.parent))
    os.makedirs(output_dir, exist_ok=True)

    rf_opts = [
        str(rp),
        f"--outputdir={output_dir}",
        "--output", f"rf_output_{int(time.time())}.xml",
        "--log", "rf_log.html",
        "--report", "rf_report.html",
    ]

    # Additional options
    if opts.get("dryrun"):
        rf_opts.append("--dryrun")
    if opts.get("console"):
        rf_opts.append("--console", opts["console"])
    verbosity = opts.get("verbosity", 1)
    if verbosity > 1:
        rf_opts.append("--verbose")
    elif verbosity == 0:
        rf_opts.append("--quiet")

    start = time.time()
    try:
        if robot_cli == "python":
            from robot import run
            exit_code = run(*rf_opts, pythonpath=str(rp.parent))
        else:
            import subprocess
            result = subprocess.run(["robot"] + rf_opts, capture_output=True, text=True, timeout=300)
            exit_code = result.returncode

        elapsed = round(time.time() - start, 2)

        # Try to parse XML result
        xml_files = list(P(output_dir).glob("rf_output_*.xml"))
        test_details: list[dict] = []
        passed = 0
        failed = 0

        if xml_files:
            try:
                # Simple XML parsing
                import xml.etree.ElementTree as ET

                tree = ET.parse(xml_files[-1])
                root = tree.getroot()
                for testCase in root.iter("test"):
                    name = testCase.get("name", "?")
                    status = testCase.get("status", "?")
                    starttime = testCase.get("starttime", "")
                    endtime = testCase.get("endtime", "")
                    msg = ""
                    for msg_el in testCase.iter("msg"):
                        msg = msg_el.text or ""
                    test_details.append({
                        "name": name,
                        "status": status,
                        "start_time": starttime,
                        "end_time": endtime,
                        "message": msg,
                    })
                    if status == "PASS":
                        passed += 1
                    else:
                        failed += 1
            except Exception:
                pass

        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "robot_file": str(rp),
            "elapsed_seconds": elapsed,
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "output_dir": output_dir,
            "output_file": str(xml_files[-1]) if xml_files else None,
            "test_details": test_details,
        }

    except subprocess.TimeoutExpired:  # type: ignore[name-defined]
        return {"success": False, "error": "Suite execution timed out (300s)", "elapsed_seconds": round(time.time() - start, 2)}
    except Exception as exc:
        return {"success": False, "error": str(exc), "elapsed_seconds": round(time.time() - start, 2)}


mcp = FastMCP(
    "Run-MCP",
)


@mcp.tool()
def run_suite_tool(suite_path: str, options: str | None = None) -> str:
    """Run a Robot Framework test suite and return execution results.

    *suite_path* - absolute or relative path to a *.robot* file.
    *options* - optional JSON string: '{"output_dir": "/tmp", "dryrun": false, "verbosity": 1, "console": "auto"}'

    Returns pass/fail counts, elapsed time, and per-test details.
    """
    opts = {}
    if options:
        try:
            opts = json.loads(options)
        except json.JSONDecodeError:
            return json.dumps({"success": False, "error": f"Invalid JSON for options: {options}"})
    result = run_suite(suite_path, opts)
    return json.dumps(result, indent=2, ensure_ascii=False)


def main():
    mcp.run(transport="stdio")
    
if __name__ == "__main__":
    main()
    