"""
Evaluation Script for PawPal+ AI System.
Runs a predefined dataset of natural language inputs against the parser
and generates a pass/fail summary report.
"""

from llm_agent import parse_task_with_llm

# Dataset de prueba (Input y Resultado Esperado)
TEST_DATASET = [
    {"input": "Walk Cooper at 7am", "expected_time": "07:00", "expected_pet": "Cooper"},
    {"input": "Feed the cat at 18:30", "expected_time": "18:30", "expected_pet": None},
    {
        "input": "Vet visit tomorrow at 2pm",
        "expected_time": "14:00",
        "expected_pet": None,
    },
    {"input": "Give water to Rocky", "expected_time": "12:00", "expected_pet": "Rocky"},
    {
        "input": "Walk Cooper at 25:00",
        "expected_time": "12:00",
        "expected_pet": "Cooper",
    },
    {"input": "Play with Luna", "expected_time": "12:00", "expected_pet": "Luna"},
    {"input": "Brush Max daily", "expected_time": "12:00", "expected_pet": "Max"},
    {
        "input": "Medication for Bella at 08:00",
        "expected_time": "08:00",
        "expected_pet": "Bella",
    },
    {"input": "Feed unknown pet", "expected_time": "12:00", "expected_pet": None},
    {"input": "Walk dog at 9:45pm", "expected_time": "21:45", "expected_pet": None},
]

KNOWN_PETS = ["Cooper", "Rocky", "Luna", "Max", "Bella"]


def run_evaluation():
    print("🧪 Starting PawPal+ AI Evaluation Harness...\n")
    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_DATASET, 1):
        text = test_case["input"]
        try:
            result = parse_task_with_llm(text, KNOWN_PETS)

            time_ok = result.time == test_case["expected_time"]
            pet_ok = result.pet_name == test_case["expected_pet"]

            if time_ok and pet_ok:
                print(
                    f"✅ Test {i} PASSED: '{text}' -> Time: {result.time}, Pet: {result.pet_name}"
                )
                passed += 1
            else:
                print(f"❌ Test {i} FAILED: '{text}'")
                print(
                    f"   Expected -> Time: {test_case['expected_time']}, Pet: {test_case['expected_pet']}"
                )
                print(f"   Got      -> Time: {result.time}, Pet: {result.pet_name}")
                failed += 1

        except Exception as e:  # noqa: BLE001
            print(f"💥 Test {i} CRASHED: '{text}' -> Error: {e}")
            failed += 1

    total = passed + failed
    accuracy = (passed / total) * 100 if total > 0 else 0

    print("\n" + "=" * 40)
    print("📊 EVALUATION SUMMARY")
    print("=" * 40)
    print(f"Total Tests : {total}")
    print(f"Passed      : {passed} ✅")
    print(f"Failed      : {failed} ❌")
    print(f"Accuracy    : {accuracy:.2f}%")
    print("=" * 40)


if __name__ == "__main__":
    run_evaluation()
