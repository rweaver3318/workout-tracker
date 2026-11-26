"""Exercise library for build_program_ron_2027.py (part 1 of 2: warm-up, legs, calves)."""


def define_library(L, yt):
    # Warm-up
    L("warm_cardio", "Easy cardio warm-up", "Warm-up",
      "Pedal the upright bike or walk on the treadmill at an easy pace, enough to feel warm and breathe a little harder but still talk easily.",
      yt("easy warm up upright bike older adults"),
      swap="No bike or treadmill (The Villages): brisk walk outside, or march in place swinging your arms.")
    L("ankle_prep", "Ankle circles and two-leg calf raises", "Warm-up",
      "Draw 10 slow circles each way with each ankle, then do easy calf raises on both feet holding a counter.",
      yt("ankle circles and calf raises warm up"))
    L("leg_swings", "Small leg swings, holding on", "Warm-up",
      "Hold a counter. Swing one leg gently forward and back, then side to side across your body, in a small, comfortable range. Never force the end of the swing.",
      yt("standing leg swings warm up hip"),
      easier="Make the swings smaller, or just march in place.")
    L("open_book", "Side-lying open book (upper-back turn)", "Warm-up",
      "Lie on your side with knees bent and stacked (a pillow between them is fine), arms straight in front. Lift the top arm up and over, turning your chest toward the ceiling and following your hand with your eyes. Breathe out as you open. This loosens the upper back for your golf turn without twisting your hips.",
      yt("side lying open book thoracic rotation"),
      easier="Do it seated: arms crossed on your chest, turn your upper body gently side to side.")
    L("pullapart", "Band pull-apart", "Warm-up",
      "Hold a light band in front of your chest with straight arms. Pull it apart until it touches your chest, squeezing your shoulder blades together and down. Return slowly.",
      yt("band pull apart exercise"))
    L("shoulder_reliever", "Shoulder Reliever circles (4 positions)", "Shoulder",
      "Hold the Shoulder Reliever handle with the ball attached and your arm extended. Keep your wrist still and make the ball circle using your shoulder, not your wrist. Circle clockwise, then counterclockwise, in each of 4 positions: (1) arm straight out in front, (2) about halfway between front and side, (3) straight out to the side, (4) bent forward at the hips with your free hand on a wall or counter and the arm hanging a little away from your body (mind your shins). Then switch arms. If shoulder height pinches, do it at waist height and let it creep up over the weeks. The maker's rules: no more than once a day, and stay on each ball at least 10 days and until shoulder height feels easy in all 4 positions before moving to the next heavier ball (start the new ball back at waist height).",
      "https://www.youtube.com/watch?v=jIrns8cds04",
      easier="Lower the arm toward waist height, do fewer circles, or go back one ball.",
      swap="Shoulder Reliever not with you: loop a light band around a door handle at chest height, hold the other end with a straight arm so the band is slightly tight, and draw small, quick circles from the shoulder in the same 4 positions (same counts). Or hold a light object, like a full water bottle, and do the same small circles. Maker's how-to page: https://shoulderreliever.com/pages/instructional-video")

    # Legs, hips
    L("bridge", "Glute bridge", "Hips",
      "Lie on your back, knees bent, feet flat and hip-width. Squeeze your seat and lift your hips until your body is a straight line from knees to shoulders. Don't arch your lower back.",
      "https://www.youtube.com/watch?v=PusbZuBgeug",
      easier="Lift only halfway, or hold each rep at the top instead of doing more reps.")
    L("hip_thrust", "Bench hip thrust with a dumbbell", "Hips",
      "Sit on the floor with your upper back against the long side of the bench and a dumbbell across your hips (hold it with both hands; a folded towel under it helps). Feet flat, knees bent. Drive through your heels to lift your hips until your thighs and body are level, squeeze, then lower under control.",
      yt("dumbbell hip thrust bench beginner"),
      easier="Do floor glute bridges with the dumbbell on your hips instead.")
    L("box_squat", "Box squat to the bench", "Hips",
      "Stand in front of the bench (seat at knee height or higher) holding a dumbbell at your chest. Sit back slowly until you lightly touch the bench, pause without relaxing, then stand up. Knees follow your toes, weight in your heels, chest tall. Never go lower than the bench.",
      yt("goblet box squat to bench"),
      easier="No weight, put a firm cushion on the bench so you don't go as low, or use your hands to help push up.")
    L("wall_sit", "Shallow wall sit", "Hips",
      "Back flat on a wall, feet a step out. Slide down only until your knees are bent about a third of the way (nowhere near a chair position). Hold, weight in your heels, breathing normally.",
      yt("wall sit hold shallow knee bend"),
      easier="Slide down less, or shorten the hold.")
    L("db_hinge", "Dumbbell Romanian deadlift (hip hinge)", "Hips",
      "Stand tall with a dumbbell in each hand in front of your thighs, knees soft. Push your hips back like closing a car door with your seat, sliding the weights down your thighs to just below your knees, back flat. Stand up by squeezing your seat. The hips go back; you don't squat down.",
      yt("dumbbell romanian deadlift form beginner"),
      easier="Lighter dumbbells, or only go down to the top of your knees.")
    L("bb_rdl", "Barbell Romanian deadlift", "Hips",
      "The same hip hinge, holding the barbell. To get the bar up safely, set it on two sturdy risers (for example the step and a stack of plates) so it starts about knee height, then stand up with it. From standing, push your hips back and slide the bar down your thighs to just below the knees, back flat, then stand by squeezing your seat. Start with the bar plus light plates, and add 5 to 10 lb only when every set leaves 2 or more reps in the tank. No barbell squats, ever.",
      yt("barbell romanian deadlift form"),
      easier="Use the dumbbell Romanian deadlift instead.")
    L("bb_top_hold", "Barbell top hold (grip and posture)", "Grip",
      "Stand up with the barbell as for the Romanian deadlift and simply hold it at the top: tall, shoulders down, ribs down, squeezing the bar hard. Builds grip, forearm tendons and posture.",
      yt("barbell deadlift top hold grip"),
      easier="Hold a pair of dumbbells instead (farmer hold).")
    L("step_up", "Step-up onto the step", "Hips",
      "Put your whole foot on the step (6 to 8 inches), hand on a wall or rail. Push through that heel to stand up tall, then lower the other foot slowly back down. Finish all reps on one leg, then switch.",
      yt("step up exercise physical therapy low step"),
      easier="Use a lower step or more hand support.")
    L("step_down", "Slow step-down", "Hips",
      "Stand on the step on one leg, holding a wall. Slowly bend that knee and lower the other heel toward the floor in front, tap lightly, then stand back up. Knee over your toes, hips level. This builds the braking strength you use when you stop at the kitchen line.",
      yt("forward step down exercise physical therapy"),
      easier="Use a lower step, or only go halfway down.")
    L("split_hold", "Short split-stance hold", "Hips",
      "Stand in a short staggered stance (one foot a normal step ahead), holding a counter. Bend both knees only a few inches and hold, with your weight mostly on the front leg. No deep lunges.",
      yt("split squat isometric hold supported"),
      easier="Bend less, lean more on the counter, or shorten the hold.")
    L("sl_rdl", "Single-leg Romanian deadlift, hand on the wall", "Balance",
      "Stand on one leg, fingertips on a wall or counter. Hinge forward at the hips as the free leg reaches straight back, hips level and back flat, only as far as is comfortable, then stand up tall. Great for balance, hips and golf posture.",
      yt("single leg romanian deadlift supported wall"),
      easier="Keep the back toe on the floor like a kickstand, and hinge less.")
    L("side_leg_lift", "Side-lying leg lift", "Hips",
      "Lie on your side, bottom knee bent, top leg straight and slightly behind you, toes pointing forward. Lift the top leg about a foot, pause, lower slowly. Don't roll backward.",
      "https://www.youtube.com/watch?v=mxWissvKVj0",
      easier="Lift lower, or bend the top knee to shorten the lever.")
    L("clamshell", "Clamshell with band", "Hips",
      "Lie on your side, hips and knees bent, a band just above your knees. Keep your feet together and open the top knee like a clamshell, without rolling backward. Pause, close slowly.",
      yt("side lying clamshell exercise band"),
      easier="No band, and a smaller opening.")
    L("wall_press_hold", "Side hip wall press hold", "Hips",
      "Stand side-on to a wall, about a hand's width away. Lift the knee nearest the wall to hip height (or lower) and press the outside of that knee into the wall while standing tall on the other leg. Both hips work hard. Hold, then switch sides.",
      yt("standing hip abduction isometric wall press"),
      easier="Lift the knee less, press more gently, or hold a counter with the other hand.")
    L("band_walk", "Side-step band walk", "Hips",
      "Band just above your knees. Knees slightly bent, chest tall. Step sideways with control, keeping tension on the band, toes pointing forward.",
      yt("lateral band walk exercise"),
      easier="Lighter band and smaller steps.")
    L("adductor_squeeze", "Inner-thigh squeeze hold", "Hips",
      "Lie on your back, knees bent, a firm pillow or rolled towel between your knees. Squeeze and hold, breathing normally. Builds the inner-thigh strength you need for side-to-side pickleball moves.",
      yt("adductor squeeze isometric ball between knees"),
      easier="Squeeze more gently.")
    L("adductor_side_plank", "Inner-thigh side plank, knee on the bench", "Hips",
      "Lie on your side next to the bench, propped on your elbow, with the inside of your top knee resting on the bench and the bottom leg hanging. Lift your hips so your body is straight and hold. Short-lever version only.",
      yt("short lever copenhagen plank knee on bench"),
      easier="Do the inner-thigh squeeze hold instead.", optional=True)

    # Calves
    L("calf_hold", "Calf raise hold", "Calf",
      "Hold a counter. Rise onto the balls of your feet to about halfway up and hold there, steady, without bouncing. Single-leg when the workout says so (lift the other foot behind you). The right calf is still a bit weaker, so it gets the extra set. When the workout lists a dumbbell, hold it in the same-side hand.",
      yt("isometric calf raise hold single leg"),
      easier="Two legs instead of one, a lower height, or less time.")
    L("calf_slow", "Slow calf raise, straight knee", "Calf",
      "Hold a counter. Rise as high as you can over 3 seconds, hold a moment, and lower over 3 seconds. When the workout says 'step edge', stand on the edge of the step so your heel can drop a little below it at the bottom. Add a dumbbell in the same-side hand as you get stronger. This heavy, slow calf work rebuilds the tendon.",
      yt("slow single leg calf raise off step"),
      easier="Do it on the flat floor, or on two legs.")
    L("calf_bent", "Bent-knee calf raise (seated with dumbbells)", "Calf",
      "Sit on the bench with the balls of your feet on a plate or the step and dumbbells resting on your knees (hands holding them steady). Lift your heels as high as you can, hold a moment, and lower slowly. This works the lower calf muscle (the soleus), which matters a lot for pickleball footwork.",
      yt("seated calf raise with dumbbells"),
      easier="Lighter dumbbells, or no step under your feet.")
    L("quick_feet", "Quick feet in place", "Footwork",
      "Ready position (knees soft, weight on the balls of your feet). Take fast, tiny steps in place with your feet barely leaving the floor. Light and quiet.",
      yt("quick feet drill in place"),
      easier="Slower steps, or brisk marching.")
    L("pogo", "Small two-foot ankle hops", "Footwork",
      "Only once you pass the hop checklist in the notes. On both feet, in shoes, on a forgiving surface: small quick hops from the ankles, 1 to 2 inches off the floor, knees nearly straight, landing quietly. Stop at the first sign of calf or hip pain.",
      yt("pogo hops low amplitude"),
      easier="Quick feet in place instead (no hopping).")
    L("line_hops", "Small side-to-side line hops", "Footwork",
      "Only once you pass the hop checklist. Feet together, hop a few inches side to side over a line, landing softly and quietly. Small and quick, not high.",
      yt("lateral line hops two feet"),
      easier="Quick side-steps over the line instead (no hop).", optional=True)

    from ron2027_library2 import define_library2
    define_library2(L, yt)
