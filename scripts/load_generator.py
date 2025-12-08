"""
Load generator for creating realistic incident scenarios

Usage:
    python scripts/load_generator.py --url http://localhost:8000
"""

import requests
import time
import random
import argparse
from datetime import datetime


def print_banner():
    print("\n" + "="*60)
    print("🔥 Incident Simulation Load Generator")
    print("="*60 + "\n")


def generate_normal_traffic(base_url: str, count: int = 10):
    """Generate normal traffic (baseline)"""
    print(f"📊 Generating {count} normal requests...")
    
    success_count = 0
    error_count = 0
    
    for i in range(count):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print(f"  [{i+1}/{count}] ✅ Normal request - {response.status_code}")
                success_count += 1
            else:
                print(f"  [{i+1}/{count}] ⚠️  Unexpected status - {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  [{i+1}/{count}] ❌ Connection failed - is the server running?")
            error_count += 1
        except requests.exceptions.Timeout:
            print(f"  [{i+1}/{count}] ❌ Request timeout")
            error_count += 1
        except Exception as e:
            print(f"  [{i+1}/{count}] ❌ Error: {type(e).__name__}: {e}")
            error_count += 1
        
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"  Summary: {success_count} success, {error_count} errors")


def simulate_db_exhaustion(base_url: str, count: int = 3):
    """Simulate database connection pool exhaustion"""
    print(f"\n🔴 Simulating DB exhaustion ({count} times)...")
    
    for i in range(count):
        try:
            response = requests.post(
                f"{base_url}/simulate/db-exhaustion",
                timeout=10
            )
            result = response.json()
            print(f"  [{i+1}/{count}] DB exhaustion simulated")
            print(f"    - Logs generated: {result.get('logs_generated', 0)}")
            print(f"    - Duration: {result.get('duration_ms', 0)}ms")
            print(f"    - Trace ID: {result.get('trace_id', 'N/A')}")
        except requests.exceptions.Timeout:
            print(f"  [{i+1}/{count}] ❌ Request timeout (expected for slow simulation)")
        except Exception as e:
            print(f"  [{i+1}/{count}] ❌ Error: {type(e).__name__}: {e}")
        
        time.sleep(2)


def simulate_high_latency(base_url: str, count: int = 2):
    """Simulate high latency issues"""
    print(f"\n🟡 Simulating high latency ({count} times)...")
    
    for i in range(count):
        try:
            response = requests.post(
                f"{base_url}/simulate/high-latency",
                timeout=10
            )
            result = response.json()
            print(f"  [{i+1}/{count}] High latency simulated")
            print(f"    - Logs generated: {result.get('logs_generated', 0)}")
            print(f"    - Duration: {result.get('duration_ms', 0)}ms")
            print(f"    - Trace ID: {result.get('trace_id', 'N/A')}")
        except requests.exceptions.Timeout:
            print(f"  [{i+1}/{count}] ❌ Request timeout")
        except Exception as e:
            print(f"  [{i+1}/{count}] ❌ Error: {type(e).__name__}: {e}")
        
        time.sleep(2)


def simulate_memory_leak(base_url: str, count: int = 2):
    """Simulate memory leak scenarios"""
    print(f"\n🟣 Simulating memory leak ({count} times)...")
    
    for i in range(count):
        try:
            response = requests.post(
                f"{base_url}/simulate/memory-leak",
                timeout=5
            )
            result = response.json()
            print(f"  [{i+1}/{count}] Memory leak simulated")
            print(f"    - Logs generated: {result.get('logs_generated', 0)}")
            print(f"    - Duration: {result.get('duration_ms', 0)}ms")
            print(f"    - Trace ID: {result.get('trace_id', 'N/A')}")
        except requests.exceptions.Timeout:
            print(f"  [{i+1}/{count}] ❌ Request timeout")
        except Exception as e:
            print(f"  [{i+1}/{count}] ❌ Error: {type(e).__name__}: {e}")
        
        time.sleep(2)


def simulate_multi_issue(base_url: str, count: int = 5):
    """Simulate multiple issues"""
    print(f"\n🔶 Simulating multi-issue scenario ({count} times)...")
    
    for i in range(count):
        try:
            response = requests.post(
                f"{base_url}/simulate/multi-issue",
                timeout=5
            )
            result = response.json()
            print(f"  [{i+1}/{count}] Multi-issue simulated")
            print(f"    - Logs generated: {result.get('logs_generated', 0)}")
            print(f"    - Duration: {result.get('duration_ms', 0)}ms")
            print(f"    - Trace ID: {result.get('trace_id', 'N/A')}")
        except requests.exceptions.Timeout:
            print(f"  [{i+1}/{count}] ❌ Request timeout")
        except Exception as e:
            print(f"  [{i+1}/{count}] ❌ Error: {type(e).__name__}: {e}")
        
        time.sleep(1)


def run_diagnosis(base_url: str, query: str):
    """Run diagnosis after generating load"""
    print(f"\n🔍 Running diagnosis...")
    print(f"Query: '{query}'")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/diagnose",
            json={
                "query": query,
                "time_range": "15m"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Diagnosis complete!")
            print(f"Request ID: {result['request_id']}")
            print(f"Status: {result['status']}")
            print(f"Processing Time: {result['processing_time_ms']}ms")
            print(f"Tools Executed: {len(result.get('tools_executed', []))}")
            
            # Print tool execution details
            if result.get('tools_executed'):
                print(f"\n🔧 Tools used:")
                for tool in result['tools_executed']:
                    print(f"  - {tool['tool_name']}: {tool.get('result_summary', 'N/A')} ({tool['execution_time_ms']}ms)")
            
            print(f"\n📝 Analysis:\n{result.get('analysis', 'No analysis available')}")
        else:
            print(f"❌ Diagnosis failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error detail: {error_detail}")
            except:
                print(f"Response: {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        print(f"❌ Diagnosis request timeout (>60s)")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - is the server running?")
    except Exception as e:
        print(f"❌ Error running diagnosis: {type(e).__name__}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate load for incident simulation")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API"
    )
    parser.add_argument(
        "--scenario",
        choices=["all", "db", "latency", "memory", "multi"],
        default="all",
        help="Scenario to run"
    )
    parser.add_argument(
        "--skip-diagnosis",
        action="store_true",
        help="Skip the diagnosis step after load generation"
    )
    parser.add_argument(
        "--wait-time",
        type=int,
        default=30,
        help="Seconds to wait for GCP log collection (default: 30)"
    )
    
    args = parser.parse_args()
    base_url = args.url
    
    print_banner()
    print(f"🎯 Target: {base_url}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Baseline traffic
    generate_normal_traffic(base_url, count=5)
    
    # Scenarios
    if args.scenario in ["all", "db"]:
        simulate_db_exhaustion(base_url, count=3)
    
    if args.scenario in ["all", "latency"]:
        simulate_high_latency(base_url, count=2)
    
    if args.scenario in ["all", "memory"]:
        simulate_memory_leak(base_url, count=2)
    
    if args.scenario in ["all", "multi"]:
        simulate_multi_issue(base_url, count=5)
    
    # Skip diagnosis if requested
    if args.skip_diagnosis:
        print("\n⏭️  Skipping diagnosis (--skip-diagnosis flag set)")
        print("\n" + "="*60)
        print("✅ Load generation complete!")
        print("="*60 + "\n")
        return
    
    # Wait for logs to be collected
    wait_time = args.wait_time
    print(f"\n⏳ Waiting {wait_time} seconds for logs to be collected in GCP...")
    for i in range(wait_time, 0, -1):
        print(f"  {i}s remaining...", end="\r")
        time.sleep(1)
    
    print("\n")
    
    # Run diagnosis
    run_diagnosis(
        base_url,
        "What problems occurred in the last 15 minutes? Analyze the logs and metrics."
    )
    
    print("\n" + "="*60)
    print("✅ Load generation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()