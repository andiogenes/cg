find models -name '*.obj' | while read line; do
    python culling.py "$line" & 
done
