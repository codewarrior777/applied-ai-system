"""
Evaluation Script for PawPal+ AI System.
Runs a predefined dataset against the parser and tracks LLM vs Fallback.
"""

from llm_agent import parse_task_with_llm

TEST_DATASET = [
    # ... (Mantén tu mismo dataset aquí) ...
    {"input": "Walk Cooper at 7am", "expected_time": "07:00", "expected_pet": "Cooper"},
    {"input": "Feed the cat at 18:30", "expected_time": "18:30", "expected_pet": None},
    {"input": "Vet visit tomorrow at 2pm", "expected_time": "14:00", "expected_pet": None},
    {"input": "Give water to Rocky", "expected_time": "12:00", "expected_pet": "Rocky"},
    {"input": "Walk Cooper at 25:00", "expected_time": "12:00", "expected_pet": "Cooper"},
    {"input": "Play with Luna", "expected_time": "12:00", "expected_pet": "Luna"},
    {"input": "Brush Max daily", "expected_time": "12:00", "expected_pet": "Max"},
    {"input": "Medication for Bella at 08:00", "expected_time": "08:00", "expected_pet": "Bella"},
    {"input": "Feed unknown pet", "expected_time": "12:00", "expected_pet": None},
    {"input": "Walk dog at 9:45pm", "expected_time": "21:45", "expected_pet": None},
]

KNOWN_PETS = ["Cooper", "Rocky", "Luna", "Max", "Bella"]

def run_evaluation():
    print("🧪 Starting PawPal+ AI Evaluation Harness...\n")
    
    total_tests = len(TEST_DATASET)
    passed = 0
    failed = 0
    
    # Nuevas métricas de observabilidad
    llm_success_count = 0
    fallback_count = 0

    for i, test_case in enumerate(TEST_DATASET, 1):
        text = test_case["input"]
        try:
            # Asumiendo que modificaste llm_agent.py para devolver (task, source)
            result, source = parse_task_with_llm(text, KNOWN_PETS)

            if source == "llm":
                llm_success_count += 1
            elif source == "fallback":
                fallback_count += 1

            time_ok = result.time == test_case["expected_time"]
            pet_ok = result.pet_name == test_case["expected_pet"]

            if time_ok and pet_ok:
                print(f"✅ Test {i} PASSED [{source.upper()}]: '{text}'")
                passed += 1
            else:
                print(f"❌ Test {i} FAILED [{source.upper()}]: '{text}'")
                print(f"   Expected -> Time: {test_case['expected_time']}, Pet: {test_case['expected_pet']}")
                print(f"   Got      -> Time: {result.time}, Pet: {result.pet_name}")
                failed += 1

        except Exception as e:
            print(f"💥 Test {i} CRASHED: '{text}' -> Error: {e}")
            failed += 1

    accuracy = (passed / total_tests) * 100 if total_tests > 0 else 0

    print("\n" + "=" * 50)
    print("📊 EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total Tests       : {total_tests}")
    print(f"Passed (Accuracy) : {passed} / {total_tests} ({accuracy:.2f}%)")
    print(f"Failed            : {failed}")
    print("-" * 50)
    print("🔍 AGENT OBSERVABILITY TRACE")
    print(f"LLM Handled       : {llm_success_count} tests")
    print(f"Fallback Handled  : {fallback_count} tests")
    print("=" * 50)
    
    if fallback_count > 0:
        print("⚠️  NOTE: Some tests fell back to Regex. Check if the LLM API is down")
        print("    or if Guardrails rejected malformed LLM JSON.")

if __name__ == "__main__":
    run_evaluation()