# pf67_4_copy (block 1). Touches no Fusion object. Copies into print_files_v67/_work/ the settled pieces the re-check of
#   version 67 made and sliced with (print_audit_recheck3/orient_hr/, read only), each checked by sha256 after the copy:
#   - shell_plan_blk_v3.stl: the shell's blockers v3 = the settled 14 boxes + one cylinder r 2.35 along each post insert hole
#     (D241; slicer/r3_blockers.py);
#   - shell_chin8_blk_v3.stl: the adhesion test's blockers = the chin band + the two bottom hole cylinders (D241);
#   - screen_plan_blk.stl: the screen plate's two support blockers over the peg pocket and the peg slot (D237;
#     slicer/r3_plate_blockers.py);
#   - cal_frame.stl, cal_tower.stl (print_files/calib/mkcal.py) and cal_holes_v67.stl, the hole block with the pilot lug (D242;
#     calib/r3_mkcal.py);
#   and the world->bed matrices of 2026-11-16 (print_files/_work/data/pf_2_orient.json) as data/pf_2_orient_v65.json.
#   R2_ARGS: {'files': [...]} (default: all of the above).
import shutil

R2_COPY = ('shell_plan_blk_v3.stl', 'shell_chin8_blk_v3.stl', 'screen_plan_blk.stl', 'cal_frame.stl', 'cal_tower.stl', 'cal_holes_v67.stl')


def run(_context):
    out = {}
    for f in R2_ARGS.get('files', R2_COPY):
        src = os.path.join(R2_RC3, 'orient_hr', f); dst = os.path.join(R2_DIR, 'orient', f)
        shutil.copy2(src, dst)
        a = r2_sha(src); b = r2_sha(dst)
        out[f] = [os.path.getsize(dst), b[:16], a == b]
    src = os.path.join(R2_PF65W, 'data', 'pf_2_orient.json'); dst = os.path.join(R2_DIR, 'data', 'pf_2_orient_v65.json')
    shutil.copy2(src, dst); out['pf_2_orient_v65.json'] = [os.path.getsize(dst), r2_sha(dst)[:16], r2_sha(src) == r2_sha(dst)]
    r2_out(os.path.join(R2_DIR, 'data', 'pf67_4_copy.json'), out)
    r2_log('pf67_4_copy', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
