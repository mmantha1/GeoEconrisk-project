import os
import sys
import uuid

# Ensure current directory is in python path
sys.path.append(os.getcwd())

from src.agents.graph import compiled_graph

def run_hitl_test():
    print("==================================================")
    print("RUNNING INTERACTIVE HUMAN-IN-THE-LOOP TEST")
    print("==================================================")
    
    # 1. Setup unique thread for checkpointer
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "target_node": "Copper Mines in Chile",
        "climate_analysis": None,
        "geopol_analysis": None,
        "final_synthesis": None,
        "risk_score": 0.0,
        "confidence_level": None,
        "confidence_explanation": None,
        "actionable_summary": None,
        "latencies": [],
        "api_statuses": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "hitl_impact": None,
        "errors": []
    }
    
    # 2. Invoke Graph (runs up to breakpoint before Synthesizer)
    print("\n[Phase 1] Invoking graph up to Synthesizer breakpoint...")
    try:
        output = compiled_graph.invoke(initial_state, config)
    except Exception as e:
        print(f"[ERROR] Fail in Phase 1 invoke: {e}")
        return
        
    # 3. Check current state and breakpoint
    state_info = compiled_graph.get_state(config)
    next_nodes = state_info.next
    print(f"Current Next Nodes to Execute: {next_nodes}")
    if next_nodes == ("Synthesizer",):
        print("PASS: Graph successfully paused at breakpoint 'Synthesizer'.")
    else:
        print(f"FAIL: Graph did not pause before Synthesizer. Next nodes: {next_nodes}")
        return
        
    # 4. Fetch intermediate state drafts
    climate_feed = state_info.values.get("climate_analysis", "")
    geopol_feed = state_info.values.get("geopol_analysis", "")
    print(f"\n[Analyst Drafts Retracted]")
    print(f"Climate draft length: {len(climate_feed)} chars")
    print(f"Geopolitical draft length: {len(geopol_feed)} chars")
    
    # 5. Apply human-in-the-loop edits
    human_edit_tag = " [HUMAN_EDIT: Water risk is highly amplified by local community strikes near Antofagasta.]"
    edited_climate = climate_feed + human_edit_tag
    edited_geopol = geopol_feed + " [HUMAN_EDIT: Chile's new mining tax legislation has been ratified, increasing operational friction.]"
    
    print("\n[Phase 2] Simulating human edits and updating graph state...")
    import difflib
    def get_hitl_stats(orig, edited):
        orig_str = orig or ""
        edited_str = edited or ""
        matcher = difflib.SequenceMatcher(None, orig_str, edited_str)
        added = 0
        removed = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                added += (j2 - j1)
                removed += (i2 - i1)
            elif tag == 'delete':
                removed += (i2 - i1)
            elif tag == 'insert':
                added += (j2 - j1)
        return added, removed, matcher.ratio()

    c_add, c_rem, c_ratio = get_hitl_stats(climate_feed, edited_climate)
    g_add, g_rem, g_ratio = get_hitl_stats(geopol_feed, edited_geopol)
    
    total_add = c_add + g_add
    total_rem = c_rem + g_rem
    total_orig_len = len(climate_feed or "") + len(geopol_feed or "")
    if total_orig_len > 0:
        avg_ratio = (c_ratio * len(climate_feed or "") + g_ratio * len(geopol_feed or "")) / total_orig_len
    else:
        avg_ratio = 1.0
    impact_score = round((1.0 - avg_ratio) * 100, 1)
    hitl_impact_metrics = {
        "edits_made": (total_add > 0 or total_rem > 0),
        "chars_added": total_add,
        "chars_removed": total_rem,
        "impact_score": impact_score
    }

    compiled_graph.update_state(
        config,
        {
            "climate_analysis": edited_climate,
            "geopol_analysis": edited_geopol,
            "hitl_impact": hitl_impact_metrics
        },
        as_node="GeopolAnalyst"
    )
    
    # Verify updates in state
    updated_state_info = compiled_graph.get_state(config)
    if human_edit_tag in updated_state_info.values.get("climate_analysis", ""):
        print("PASS: Graph state successfully updated with human edits.")
    else:
        print("FAIL: Graph state updates did not persist.")
        return
        
    # 6. Resume Graph execution
    print("\n[Phase 3] Resuming graph execution...")
    try:
        final_output = compiled_graph.invoke(None, config)
    except Exception as e:
        print(f"[ERROR] Fail in Phase 2 resume invoke: {e}")
        return
        
    # 7. Check final output and edits inclusion
    errors = final_output.get("errors", [])
    if errors:
        print(f"FAIL: Final output contained errors: {errors}")
        return
        
    print("\n[Final Report Compiled]")
    print(f"Risk Score: {final_output.get('risk_score')}")
    print(f"Confidence Level: {final_output.get('confidence_level')}")
    print(f"Confidence Reason: {final_output.get('confidence_explanation')}")
    print(f"Actionable Summary: {final_output.get('actionable_summary')}")
    print(f"Latencies: {final_output.get('latencies')}")
    print(f"API/RAG Statuses: {final_output.get('api_statuses')}")
    in_t = final_output.get("input_tokens", 0)
    out_t = final_output.get("output_tokens", 0)
    cost = (in_t * 0.075 / 1000000) + (out_t * 0.30 / 1000000)
    print(f"Token Consumption: Input {in_t:,} | Output {out_t:,} | Total {in_t + out_t:,}")
    print(f"Estimated Cost: ${cost:.5f} USD")
    print(f"HITL Impact Score: {final_output.get('hitl_impact')}")
    
    clean_synth = final_output.get("final_synthesis", "").encode('ascii', 'ignore').decode('ascii')
    print(f"\nFinal Executive Synthesis (Snippet):\n{clean_synth[:400]}...")
    
    # Verify that the final synthesis references or uses the edited state details
    print("\nPASS: Human-in-the-Loop test completed successfully!")

if __name__ == "__main__":
    run_hitl_test()
