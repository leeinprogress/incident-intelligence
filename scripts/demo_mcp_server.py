"""
Demo script for MCP Server Tools

This demonstrates the MCP server tools directly without running the server.
"""

import asyncio
from src.mcp_server import query_logs, query_metrics
from src.utils.logger import setup_logging, get_logger


setup_logging()
logger = get_logger(__name__)


async def test_query_logs():
    """Test the query_logs MCP tool"""
    print("\n" + "="*60)
    print("Test 1: Query Logs Tool")
    print("="*60)
    
    result = await query_logs(
        service_name="checkout-service",
        time_range="15m",
        severity="error",
        limit=10
    )
    
    print(f"\n✓ Success: {result.get('success')}")
    print(f"✓ Execution Time: {result.get('execution_time_ms')}ms")
    
    if result.get("success"):
        data = result.get("data", {})
        print(f"✓ Total Logs: {data.get('total_logs', 0)}")
        print(f"✓ Service: {data.get('service')}")
        print(f"✓ Time Range: {data.get('time_range')}")
        
        logs = data.get("logs", [])
        if logs:
            print(f"\n📋 Sample Log Entry:")
            sample = logs[0]
            print(f"  - Timestamp: {sample.get('timestamp')}")
            print(f"  - Severity: {sample.get('severity')}")
            print(f"  - Message: {sample.get('message')[:80]}...")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    print("\n" + "="*60)
    return result


async def test_query_metrics():
    """Test the query_metrics MCP tool"""
    print("\n" + "="*60)
    print("Test 2: Query Metrics Tool")
    print("="*60)
    
    result = await query_metrics(
        service_name="all",
        metric_type="all",
        time_range="15m"
    )
    
    print(f"\n✓ Success: {result.get('success')}")
    print(f"✓ Execution Time: {result.get('execution_time_ms')}ms")
    
    if result.get("success"):
        data = result.get("data", {})
        print(f"✓ Service: {data.get('service')}")
        print(f"✓ Metric Type: {data.get('metric_type')}")
        print(f"✓ Data Points: {data.get('data_points', 0)}")
        
        metrics = data.get("metrics", {})
        print(f"\n📊 Available Metrics:")
        for metric_name, datapoints in metrics.items():
            print(f"  - {metric_name}: {len(datapoints)} data points")
            if datapoints:
                latest = datapoints[-1]
                print(f"    Latest value: {latest.get('value')} at {latest.get('timestamp')}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    print("\n" + "="*60)
    return result


async def test_different_parameters():
    """Test with different parameter combinations"""
    print("\n" + "="*60)
    print("Test 3: Different Parameter Combinations")
    print("="*60)
    
    test_cases = [
        {
            "name": "All services, warnings only",
            "params": {
                "service_name": "all",
                "severity": "warning",
                "time_range": "30m"
            }
        },
        {
            "name": "Payment service, CPU metrics",
            "params": {
                "service_name": "payment-service",
                "metric_type": "cpu",
                "time_range": "1h"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n→ {test_case['name']}")
        
        if "severity" in test_case["params"]:
            # Test logs
            result = await query_logs(**test_case["params"])
            if result.get("success"):
                total = result.get("data", {}).get("total_logs", 0)
                print(f"  ✓ Found {total} logs")
            else:
                print(f"  ✗ Failed: {result.get('error')}")
        else:
            # Test metrics
            result = await query_metrics(**test_case["params"])
            if result.get("success"):
                points = result.get("data", {}).get("data_points", 0)
                print(f"  ✓ Found {points} data points")
            else:
                print(f"  ✗ Failed: {result.get('error')}")
    
    print("\n" + "="*60)


async def main():
    """Run all MCP server tool demos"""
    print("\n" + "🧪 MCP Server Tools Demo ".center(60, "="))
    print()
    
    try:
        # Run tests
        await test_query_logs()
        await test_query_metrics()
        await test_different_parameters()
        
        print("\n✅ All demos completed successfully!")
        print("\n💡 To run the actual MCP server:")
        print("   python -m src.mcp_server")
        print()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

