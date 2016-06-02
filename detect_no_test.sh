#for f in **; do [ -d "$f" ] && continue; tac "$f" | awk 'length{if($0 ~ /# Test/)exit(0);else exit(1)}' && printf %s\\n "$f"; done
#for f in *; do [ -d "$f" ] && continue; tac "$f" | awk 'length($0) > 0 {if($0 ~ /# Test/)exit(0);else exit(1)}' && printf %s\\n "$f"; done
for f in *; do [ -d "$f" ] && continue; tac "$f" | awk 'length($0) > 0 {if(/# Test/) exit(0); else exit(1)}' && printf %s\\n "$f"; done
