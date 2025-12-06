"""
Test script for DiagnosisAgent

Run this to verify the agent works correctly.
"""

import asyncio
from src.services.agent_service import DiagnosisAgent
from src.utils.logger import setup_logging


async def test_basic_diagnosis():
    """Test basic incident diagnosis"""
    print("🚀 Initializing DiagnosisAgent...")
    agent = DiagnosisAgent()
    
    print("\n" + "="*60)
    print("Test 1: Basic incident query")
    print("="*60)
    
    query = "Why is the checkout service slow?"
    print(f"\n📝 Query: {query}\n")
    
    result = await agent.diagnose(
        query=query,
        service_name="checkout-service",
        time_range="15m"
    )
    
    print("\n📊 Results:")
    print(f"Request ID: {result['request_id']}")
    print(f"Status: {result['status']}")
    print(f"Processing Time: {result['processing_time_ms']}ms")
    print(f"\nTools Executed ({len(result['tools_executed'])}):")
    for tool in result['tools_executed']:
        print(f"  - {tool['tool_name']}: {tool['result_summary']} ({tool['execution_time_ms']}ms)")
    
    print(f"\n🔍 Analysis:\n{result['analysis']}")
    
    print("\n" + "="*60 + "\n")


async def test_specific_service():
    """Test with specific service"""
    print("="*60)
    print("Test 2: Specific service query")
    print("="*60)
    
    agent = DiagnosisAgent()
    
    query = "Are there any critical errors in the payment service?"
    print(f"\n📝 Query: {query}\n")
    
    result = await agent.diagnose(
        query=query,
        service_name="payment-service",
        time_range="30m"
    )
    
    print(f"\n🔍 Analysis:\n{result['analysis']}")
    print(f"\nProcessing Time: {result['processing_time_ms']}ms")
    print("\n" + "="*60 + "\n")


async def test_general_query():
    """Test with general system query"""
    print("="*60)
    print("Test 3: General system health check")
    print("="*60)
    
    agent = DiagnosisAgent()
    
    query = "What's the overall system health? Are there any issues?"
    print(f"\n📝 Query: {query}\n")
    
    result = await agent.diagnose(
        query=query,
        time_range="1h"
    )
    
    print(f"\n🔍 Analysis:\n{result['analysis']}")
    print(f"\nTools Executed: {len(result['tools_executed'])}")
    print("\n" + "="*60 + "\n")


async def main():
    """Run all tests"""
    print("\n" + "🧪 Testing DiagnosisAgent ".center(60, "="))
    print()
    
    # Setup logging
    setup_logging()
    
    try:
        # Run tests
        await test_basic_diagnosis()
        await test_specific_service()
        await test_general_query()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())