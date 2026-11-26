"""Exercise library part 2: upper body, shoulder, bar, elbow and grip."""

BAR_SWAP = ("No pull-up bar (The Villages): band pulldown hold. Anchor a band high in a door. Kneel or sit, pull your elbows down to your sides "
            "so your hands are at shoulder level, squeeze your shoulder blades down, and hold.")


def define_library2(L, yt):
    L("incline_pushup", "Incline push-up on the bench or counter", "Upper",
      "Hands on the edge of the bench or a counter, body in a straight line. Lower your chest toward it, elbows angled back about 45 degrees, then push away. The higher your hands, the easier it is.",
      yt("incline push up on bench"), easier="Use a higher surface (counter or wall).")
    L("pushup_plus", "Incline push-up plus", "Shoulder",
      "Do an incline push-up, and at the top push a little further so your shoulder blades spread around your ribs (your upper back rounds slightly). That last bit works the muscle that keeps the shoulder blade snug on the ribs.",
      yt("push up plus exercise serratus"), easier="Do it against a wall.")
    L("incline_press", "Incline bench dumbbell press", "Upper",
      "Set the bench to a low incline. Lie back with a dumbbell in each hand at chest level, elbows angled back about 45 degrees. Press up until your arms are straight, then lower slowly.",
      yt("incline dumbbell press form"), easier="Lighter dumbbells, or incline push-ups.")
    L("db_row", "Bench-supported one-arm row", "Upper",
      "One hand on the bench with both feet on the floor (kinder to the hips than kneeling on the bench), back flat. Pull the dumbbell toward your hip, squeezing the shoulder blade back and down, then lower slowly.",
      yt("one arm dumbbell row bench supported"), easier="Lighter dumbbell, or a band row anchored in a door.")
    L("face_pull", "Band face pull", "Shoulder",
      "Anchor a band at head height. Hold both ends, thumbs pointing back. Pull toward your face with elbows high and wide, finishing with your hands beside your ears as if showing off your biceps. Return slowly.",
      yt("band face pull exercise"))
    L("er_side", "Band outward rotation, elbow at your side", "Shoulder",
      "Band anchored at elbow height to your side. Elbow bent 90 degrees and tucked against your side (a rolled towel under the arm helps). Rotate your forearm outward, away from your belly, keeping the elbow in place, then return slowly.",
      "https://www.youtube.com/watch?v=_UvmPNGtlPM", easier="Lighter band, smaller range.")
    L("er_hold", "Outward rotation hold in a doorway", "Shoulder",
      "Stand in a doorway with your elbow bent 90 degrees at your side and the back of your wrist against the door frame. Press outward into the frame (nothing moves) and hold.",
      yt("isometric shoulder external rotation doorway"), easier="Press more gently.")
    L("er_goalpost", "Band outward rotation, arm out to the side", "Shoulder",
      "Band anchored in front of you at shoulder height. Raise your upper arm out to the side to shoulder height with the elbow bent 90 degrees and the forearm pointing forward (like a goalpost). Rotate the forearm up until it points to the ceiling, then lower slowly. This is the position you serve and hit overheads from.",
      yt("band 90 90 external rotation exercise"),
      easier="Keep the elbow a bit below shoulder height, or use the elbow-at-your-side version.")
    L("y_raise", "Incline bench Y raise", "Shoulder",
      "Set the bench to a medium incline and lie face down on it, arms hanging, thumbs up. Raise your arms up and out in a Y to about ear level, squeezing your shoulder blades down, then lower slowly. Start with no weight; use the 10 lb dumbbells only when it's easy.",
      yt("incline prone y raise"),
      easier="Raise to a T (straight out to the sides) instead, or stand and use a light band.")
    L("overhead_hold", "Overhead dumbbell hold", "Shoulder",
      "Press one dumbbell overhead and hold it there with a straight arm, biceps near your ear, ribs down, standing tall (walk slowly if you like). Builds overhead shoulder tolerance.",
      yt("single arm overhead dumbbell hold waiter carry"),
      easier="Hold the dumbbell at shoulder height instead, or use a light band overhead.")
    L("db_press", "Standing one-arm dumbbell press", "Shoulder",
      "Stand tall, a dumbbell at your shoulder, palm facing in. Press straight up without leaning back, then lower slowly.",
      yt("standing single arm dumbbell shoulder press"),
      easier="Sit on the bench with the back upright, or go lighter.")
    L("wall_slide", "Wall slide with band", "Shoulder",
      "Face a wall with your forearms on it and a light band around your wrists. Push gently outward into the band and slide your forearms up the wall as high as is comfortable, then back down.",
      yt("wall slide with band serratus"), easier="No band, and only partway up.")

    L("dead_hang", "Dead hang with feet helping", "Bar",
      "Grip the pull-up bar shoulder-width. Keep your feet on a step or the floor taking some of your weight, and let your body hang with your shoulders gently engaged (not shrugged to your ears). Take a little more weight off your feet over the weeks.",
      yt("assisted dead hang feet on floor"), easier="More weight on your feet, or shorter holds.",
      swap=BAR_SWAP, optional=True, where="Fayetteville")
    L("scap_hang", "Shoulder-blade pull on the bar", "Bar",
      "Hang from the bar (feet helping if needed). Without bending your elbows, pull your shoulder blades down and back so your body rises an inch, hold 3 seconds, then relax back to the hang.",
      yt("scapular pull up hang"), easier="Keep more weight on your feet.",
      swap=BAR_SWAP, optional=True, where="Fayetteville")
    L("top_hold", "Top-of-pull-up hold", "Bar",
      "Use a step or chair to get your chin over the bar (or as high as you can), then take your feet away and hold, elbows bent, chest up. Step back down; don't drop.",
      yt("flexed arm hang hold"), easier="Hold with the elbows bent halfway, or keep a toe on the step.",
      swap=BAR_SWAP, optional=True, where="Fayetteville")
    L("slow_lower", "Slow pull-up lowering", "Bar",
      "Step up so your chin is over the bar, take your feet away, then lower yourself as slowly as you can (aim for 4 to 5 seconds) to a straight-arm hang. Step back up and repeat. The quickest route from 1 pull-up to several.",
      yt("pull up negatives slow lowering"), easier="Top-of-pull-up hold instead, or lower with a toe on the chair.",
      swap="No pull-up bar: slow band pulldown. Anchor the band high, pull your elbows down to your sides, then let the band pull your arms back up over 4 seconds.",
      optional=True, where="Fayetteville")

    L("wrist_flex_hold", "Palm-up wrist hold (inner elbow tendon)", "Elbow",
      "Sit with your forearm resting on your thigh or the bench, palm up, hand just past the edge, holding a dumbbell. Keep the wrist level and still. This loads the inner-elbow tendon gently and often eases golfer's elbow pain. The right arm gets the extra set.",
      yt("isometric wrist flexion hold dumbbell golfers elbow"),
      easier="Press your palm up into the underside of a table instead of holding a dumbbell, or press gently.")
    L("pronation_hold", "Forearm turn-in hold", "Elbow",
      "Sit with your forearm on your thigh, elbow bent, holding a dumbbell by one end only, like a hammer, standing upright. Let the palm turn slightly toward the floor so the weight leans inward, and hold it there without moving. Choke up on the handle to make it easier.",
      yt("isometric forearm pronation hold dumbbell"),
      easier="Hold closer to the weighted end, or press your hand against your other hand.")
    L("wrist_flex_lower", "Slow palm-up wrist lowering", "Elbow",
      "Forearm on your thigh or the bench, palm up, dumbbell in hand. Use your other hand to help lift the weight up (wrist curled), then let go and lower it slowly with just the working hand over 4 seconds. Help it back up and repeat. This slow-lowering type of loading is what helped golfer's elbow in the research. If you get a rubber FlexBar (about $20), the Reverse Tyler Twist can replace this: https://www.youtube.com/watch?v=LtR8fYEUnXI",
      yt("eccentric wrist flexion exercise golfers elbow"),
      easier="Lighter dumbbell or a shorter range.")
    L("pronation_lower", "Slow forearm turn-in lowering", "Elbow",
      "Hold the dumbbell by one end like a hammer, forearm on your thigh. Use the other hand to help turn the palm up, then let go and slowly let the palm turn back down toward the floor over 3 to 4 seconds, resisting with your forearm. Help it back and repeat.",
      yt("eccentric pronation exercise dumbbell hammer"),
      easier="Hold the handle closer to the weighted end.")
    L("farmer_hold", "Farmer hold", "Grip",
      "Hold a dumbbell in each hand at your sides. Stand tall, shoulders down and back, and squeeze the handles. Walk slowly if you like.",
      yt("farmer hold carry dumbbell"), easier="Lighter dumbbells or shorter holds.")
    L("suitcase_hold", "One-arm suitcase hold", "Core",
      "Hold one heavy dumbbell at your side like a suitcase and stand perfectly straight, not leaning. Walk slowly if you like. Works grip and the side core muscles that stop you tipping.",
      yt("suitcase carry dumbbell"), easier="Lighter dumbbell.")

    from ron2027_library3 import define_library3
    define_library3(L, yt)
