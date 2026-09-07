import os
import sys
import json

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend path is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.rag.retriever import Retriever
from backend.rag.answer_engine import AnswerEngine

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation():
    print("=" * 70)
    print("       RuleGuard AI -- Automated Evaluation Suite")
    print("=" * 70)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    test_data_dir = os.path.join(base_dir, "test_data")

    normal_qs = load_json(os.path.join(test_data_dir, "normal_questions.json"))
    conflict_qs = load_json(os.path.join(test_data_dir, "conflict_questions.json"))
    not_covered_qs = load_json(os.path.join(test_data_dir, "not_covered_questions.json"))

    retriever = Retriever()
    if not retriever.loaded:
        print("ERROR: Vector index is not loaded. Run build_index.py first.")
        sys.exit(1)

    answer_engine = AnswerEngine()

    total_passed = 0
    total_questions = 0

    categories = [
        ("ANSWERED (Normal)", normal_qs),
        ("CONFLICT (Planted Contradictions)", conflict_qs),
        ("NOT_COVERED (Out of Scope)", not_covered_qs)
    ]

    for cat_name, qs in categories:
        print(f"\n--- Evaluating Category: {cat_name} ({len(qs)} questions) ---")
        cat_passed = 0

        for q_item in qs:
            qid = q_item["id"]
            question = q_item["question"]
            expected = q_item["expected_status"]

            retrieved = retriever.retrieve(question, top_k=6)
            res = answer_engine.process_query(question, retrieved)
            actual = res.status

            is_pass = (actual == expected)
            if is_pass:
                cat_passed += 1
                total_passed += 1
                status_icon = "[PASS]"
            else:
                status_icon = "[FAIL]"

            print(f"{status_icon} {qid} | Expected: {expected.upper():<12} | Predicted: {actual.upper():<12}")
            print(f"       Q: \"{question}\"")
            if not is_pass:
                top_sim = max(s["similarity"] for s in retrieved) if retrieved else 0.0
                print(f"       Debug Top Similarity: {top_sim}")

            total_questions += 1

        print(f" -> Category Score: {cat_passed} / {len(qs)} passed ({(cat_passed/len(qs))*100:.1f}%)")

    print("\n" + "=" * 70)
    print("                     EVALUATION SUMMARY")
    print("=" * 70)
    print(f" Total Tests Run: {total_questions}")
    print(f" Total Passed:    {total_passed}")
    print(f" Overall Accuracy: {(total_passed / total_questions) * 100:.2f}%")
    print("=" * 70)

if __name__ == "__main__":
    run_evaluation()
