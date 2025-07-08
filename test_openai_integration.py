#!/usr/bin/env python3
"""
Enhanced Integration Test for OpenAI Integration
Tests both OpenAI enhanced features and fallback functionality
"""

import asyncio
import aiohttp
import json
import time
import os
from typing import Dict, Any

class OpenAIIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:12000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_ai_status(self) -> Dict[str, Any]:
        """Test AI service status endpoint"""
        print("🔍 Testing AI Service Status...")
        
        try:
            async with self.session.get(f"{self.base_url}/ai/status") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ AI Status Check: {result}")
                    return {"status": "passed", "data": result}
                else:
                    error_msg = f"Status check failed with code {response.status}"
                    print(f"❌ AI Status Check Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            print(f"❌ AI Status Check Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_enhanced_learning_style_analysis(self) -> Dict[str, Any]:
        """Test enhanced learning style analysis"""
        print("🧠 Testing Enhanced Learning Style Analysis...")
        
        test_data = {
            "user_responses": [
                "I prefer visual diagrams and interactive examples",
                "I learn better with hands-on practice and real projects",
                "I need quiet environment to focus and take detailed notes"
            ]
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/analyze-learning-style-enhanced",
                json=test_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Enhanced Learning Style Analysis: {result.get('primary_style', 'unknown')} "
                          f"(confidence: {result.get('confidence', 0):.2f}) "
                          f"[{result.get('source', 'unknown')}]")
                    return {"status": "passed", "data": result}
                else:
                    error_msg = f"Analysis failed with code {response.status}"
                    print(f"❌ Enhanced Learning Style Analysis Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ Enhanced Learning Style Analysis Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_enhanced_content_generation(self) -> Dict[str, Any]:
        """Test enhanced content generation"""
        print("📚 Testing Enhanced Content Generation...")
        
        test_data = {
            "topic": "Python Functions",
            "learning_style": "visual",
            "difficulty_level": "intermediate",
            "user_preferences": ["interactive", "examples", "practice"]
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/generate-content-enhanced",
                json=test_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content_length = len(str(result.get('content', '')))
                    print(f"✅ Enhanced Content Generation: Generated {content_length} chars "
                          f"for {test_data['topic']} [{result.get('source', 'unknown')}]")
                    return {"status": "passed", "data": result}
                else:
                    error_msg = f"Content generation failed with code {response.status}"
                    print(f"❌ Enhanced Content Generation Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ Enhanced Content Generation Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_enhanced_recommendations(self) -> Dict[str, Any]:
        """Test enhanced recommendations"""
        print("🎯 Testing Enhanced Recommendations...")
        
        test_data = {
            "user_id": "test_user",
            "user_profile": {
                "learning_style": "kinesthetic",
                "experience_level": "intermediate",
                "interests": ["programming", "web development"]
            },
            "performance_data": {
                "accuracy": 0.85,
                "completion_rate": 0.92,
                "time_spent": 3600,
                "topics_completed": ["variables", "functions", "loops"]
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/recommendations-enhanced",
                json=test_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    num_recs = len(result.get('recommendations', []))
                    print(f"✅ Enhanced Recommendations: Generated {num_recs} recommendations "
                          f"[{result.get('source', 'unknown')}]")
                    return {"status": "passed", "data": result}
                else:
                    error_msg = f"Recommendations failed with code {response.status}"
                    print(f"❌ Enhanced Recommendations Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ Enhanced Recommendations Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_quiz_generation(self) -> Dict[str, Any]:
        """Test quiz generation (OpenAI only feature)"""
        print("📝 Testing Quiz Generation...")
        
        test_data = {
            "topic": "Python Loops",
            "difficulty_level": "beginner",
            "learning_style": "visual",
            "num_questions": 3
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/generate-quiz",
                json=test_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    num_questions = len(result.get('questions', []))
                    print(f"✅ Quiz Generation: Generated {num_questions} questions "
                          f"for {test_data['topic']}")
                    return {"status": "passed", "data": result}
                elif response.status == 503:
                    print("ℹ️ Quiz Generation: Requires OpenAI integration (expected if not configured)")
                    return {"status": "skipped", "reason": "OpenAI not available"}
                else:
                    error_msg = f"Quiz generation failed with code {response.status}"
                    print(f"❌ Quiz Generation Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ Quiz Generation Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_batch_processing(self) -> Dict[str, Any]:
        """Test batch AI processing"""
        print("⚡ Testing Batch AI Processing...")
        
        test_data = {
            "user_responses": [
                "I prefer visual learning with diagrams",
                "I like interactive coding exercises"
            ],
            "topic": "Python Basics",
            "learning_style": "visual",
            "difficulty_level": "beginner",
            "user_profile": {
                "learning_style": "visual",
                "experience_level": "beginner"
            },
            "performance_data": {
                "accuracy": 0.75,
                "completion_rate": 0.8
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/batch-analysis",
                json=test_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    results_count = len(result.get('results', {}))
                    print(f"✅ Batch Processing: Processed {results_count} AI operations")
                    return {"status": "passed", "data": result}
                else:
                    error_msg = f"Batch processing failed with code {response.status}"
                    print(f"❌ Batch Processing Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ Batch Processing Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_ai_capabilities(self) -> Dict[str, Any]:
        """Test AI capabilities endpoint"""
        print("🔧 Testing AI Capabilities...")
        
        try:
            async with self.session.get(f"{self.base_url}/ai/capabilities") as response:
                if response.status == 200:
                    result = await response.json()
                    openai_available = result.get('openai_status', {}).get('available', False)
                    print(f"✅ AI Capabilities: OpenAI {'Available' if openai_available else 'Not Available'}")
                    return {"status": "passed", "data": result}
                else:
                    error_msg = f"Capabilities check failed with code {response.status}"
                    print(f"❌ AI Capabilities Failed: {error_msg}")
                    return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ AI Capabilities Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def test_fallback_comparison(self) -> Dict[str, Any]:
        """Test comparison between enhanced and fallback modes"""
        print("🔄 Testing Enhanced vs Fallback Comparison...")
        
        test_responses = ["I prefer visual learning with interactive examples"]
        
        try:
            # Test enhanced endpoint
            async with self.session.post(
                f"{self.base_url}/ai/analyze-learning-style-enhanced",
                json={"user_responses": test_responses}
            ) as response:
                enhanced_result = await response.json() if response.status == 200 else None
            
            # Test fallback endpoint
            async with self.session.post(
                f"{self.base_url}/ai/analyze-learning-style",
                json={"user_responses": test_responses}
            ) as response:
                fallback_result = await response.json() if response.status == 200 else None
            
            if enhanced_result and fallback_result:
                enhanced_source = enhanced_result.get('source', 'unknown')
                fallback_source = 'fallback'
                
                print(f"✅ Comparison: Enhanced [{enhanced_source}] vs Fallback [{fallback_source}]")
                return {
                    "status": "passed",
                    "data": {
                        "enhanced": enhanced_result,
                        "fallback": fallback_result,
                        "comparison": {
                            "enhanced_source": enhanced_source,
                            "fallback_source": fallback_source
                        }
                    }
                }
            else:
                print("❌ Comparison Failed: Could not get results from both endpoints")
                return {"status": "failed", "error": "Could not compare endpoints"}
                
        except Exception as e:
            error_msg = f"Comparison failed: {str(e)}"
            print(f"❌ Comparison Failed: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting OpenAI Integration Tests\n")
        
        tests = [
            ("AI Status", self.test_ai_status),
            ("Enhanced Learning Style Analysis", self.test_enhanced_learning_style_analysis),
            ("Enhanced Content Generation", self.test_enhanced_content_generation),
            ("Enhanced Recommendations", self.test_enhanced_recommendations),
            ("Quiz Generation", self.test_quiz_generation),
            ("Batch Processing", self.test_batch_processing),
            ("AI Capabilities", self.test_ai_capabilities),
            ("Enhanced vs Fallback", self.test_fallback_comparison)
        ]
        
        results = {}
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                
                if result["status"] == "passed":
                    passed += 1
                elif result["status"] == "skipped":
                    skipped += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"❌ {test_name} Failed: {str(e)}")
                results[test_name] = {"status": "failed", "error": str(e)}
                failed += 1
            
            print()  # Add spacing between tests
        
        # Print summary
        total = passed + failed + skipped
        print("=" * 60)
        print(f"📊 OpenAI Integration Test Results: {passed}/{total} PASSED")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️ Skipped: {skipped}")
        
        if failed == 0:
            print("🎉 All available tests passed!")
        elif passed > 0:
            print("⚠️ Some tests passed, check failed tests above.")
        else:
            print("💥 All tests failed. Please check the backend server and configuration.")
        
        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": passed / total if total > 0 else 0
            },
            "results": results
        }

async def main():
    """Main test runner"""
    print("🧠 Powered Adaptive Learning App - OpenAI Integration Test Suite")
    print("=" * 60)
    
    # Check if OpenAI API key is configured
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"🔑 OpenAI API Key: Configured (length: {len(openai_key)})")
    else:
        print("⚠️ OpenAI API Key: Not configured (fallback mode will be used)")
    
    print()
    
    async with OpenAIIntegrationTester() as tester:
        results = await tester.run_all_tests()
        
        # Save results to file
        with open("openai_integration_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: openai_integration_test_results.json")
        
        return results["summary"]["success_rate"] > 0.5

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)