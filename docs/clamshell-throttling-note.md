# macOS Clamshell Mode CPU Throttling

## Issue Discovered: November 26, 2025

During overnight batch processing with the MacBook lid closed (clamshell mode), processing speed dropped dramatically despite using `caffeinate -i` to prevent sleep.

## Observed Behavior

| Condition | Batch Time (100 images) |
|-----------|------------------------|
| Lid open | ~13-14 minutes |
| Clamshell mode | 1.3 - 2.5 hours |

During a 6-hour clamshell period (10 PM - 4 AM), only ~500 images were processed instead of the expected ~2,500-2,700.

## Why This Happens

`caffeinate -i` prevents **idle sleep** but does NOT prevent **thermal throttling**.

When the lid is closed:
1. **No airflow** - The keyboard area provides significant ventilation; closing the lid blocks this
2. **Heat buildup** - CPU generates heat with nowhere to go
3. **Thermal management** - macOS aggressively reduces CPU frequency to prevent overheating
4. **Result** - CPU runs at minimum frequency, dramatically slowing compute-intensive tasks

## Why an External Monitor Helps

When an external display is connected and the lid is closed, macOS enters **clamshell display mode** rather than treating it as "preparing to sleep":

1. **System stays in "active use" state** - macOS recognizes you're actively using the computer
2. **Higher performance tier** - The system maintains higher CPU frequencies because it expects interactive workloads
3. **Better thermal budget** - macOS allows higher temperatures when it knows the system is in use
4. **GPU stays active** - Keeps the system in a higher power state overall

However, even with an external monitor, thermal throttling can still occur due to reduced airflow. The best solutions for long batch jobs:

1. **Keep the lid open** - Even slightly propped open improves airflow significantly
2. **Use a laptop stand** - Elevates the machine for better ventilation
3. **External monitor + lid open** - Best of both worlds
4. **Cooling pad** - Active cooling can help maintain performance

## Recommendations for Overnight Batch Processing

- Keep the lid at least partially open
- Use a cooling pad for extended processing
- Monitor temperatures with `sudo powermetrics --samplers smc` if needed
- Consider scheduling heavy batch jobs during times when you can leave the lid open
