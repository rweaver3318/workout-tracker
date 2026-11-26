"""Exercise library part 3: core, rotation, balance, footwork, cool-down, retests."""


def define_library3(L, yt):
    L("dead_bug", "Dead bug", "Core",
      "Lie on your back, arms up, knees bent over your hips. Press your lower back gently into the floor. Slowly reach one arm overhead and straighten the opposite leg toward the floor, then return and switch. Keep your back flat.",
      yt("dead bug exercise beginner"), easier="Move only the arms, or tap a heel to the floor with the knee bent.")
    L("side_plank", "Side plank", "Core",
      "Lie on your side propped on your elbow, elbow under your shoulder. Lift your hips so your body is straight from head to knees (knees bent) or, later, head to feet. Hold.",
      yt("side plank knees bent beginner"), easier="Knees bent, or lean on the bench at an angle.")
    L("pallof_hold", "Band anti-rotation hold (Pallof hold)", "Core",
      "Anchor a band at chest height to your side. Stand side-on, feet hip-width, holding the band at your chest with both hands. Press your hands straight out and hold, not letting the band turn you. This trains your core to resist twisting, which protects your back in golf and pickleball.",
      yt("pallof press hold band"), easier="Step closer to the anchor for less tension.")
    L("pallof_press", "Band anti-rotation press (Pallof press)", "Core",
      "Same setup as the hold. Press the band out, hold, bring it back, staying square the whole time.",
      yt("pallof press band exercise"), easier="Step closer to the anchor.")
    L("band_chop", "Band chop, high to low", "Rotation",
      "Band anchored high to one side. Hold it with both hands and pull it down and across your body to the opposite hip, turning your chest and letting your back heel pivot so your hips turn together with your shoulders (no twisting at the hip joint). Return slowly. Smooth, not jerky.",
      yt("band wood chop high to low"), easier="Lighter band, smaller range.")
    L("band_lift", "Band lift, low to high", "Rotation",
      "Band anchored low to one side. Pull it up and across your body to the opposite shoulder, turning your chest and pivoting your back foot, then return slowly. Like a forehand drive.",
      yt("band low to high lift rotation"), easier="Lighter band, smaller range.")
    L("fast_chop", "Fast band chop or lift", "Rotation",
      "Same as the band chop or lift, but pull quickly and smoothly, then return slowly over 3 seconds. Stay balanced, feet pivoting together. Builds swing speed safely.",
      yt("explosive band rotation chop"), easier="Moderate speed, lighter band.")
    L("golf_turn", "Golf-posture turn with a club", "Rotation",
      "Hold a club across your chest and take your golf posture. Turn your upper body back and through slowly, letting your hips turn naturally with you. Then make a few slow practice swings, pausing at the top for 2 seconds.",
      yt("golf thoracic rotation drill club across chest"), easier="Stand taller and turn less.")

    L("sl_balance", "Single-leg balance", "Balance",
      "Stand on one leg next to a counter, knee soft. The workout tells you which version: eyes open, slow head turns, tossing a ball hand to hand, or eyes closed (only with a counter right there).",
      yt("single leg balance progression older adults"), easier="Lightly touch the counter or the other toe down.")
    L("side_stick", "Side step and stick", "Footwork",
      "From a ready position, take one big step to the side, land softly with the knee bent over your toes, and hold still for 2 seconds. Step back and repeat. Teaches braking when you reach for a wide ball.",
      yt("lateral step and stick deceleration"), easier="Smaller steps, hand near a counter.")
    L("shuffle_stop", "Shuffle and stop", "Footwork",
      "Shuffle 2 or 3 steps sideways, then stop firmly on the outside leg and hold for 2 seconds. Go back the other way. Quick feet, quiet stops.",
      yt("lateral shuffle and stop deceleration drill"), easier="Walk the steps instead of shuffling.")
    L("split_step", "Pickleball split step and react", "Footwork",
      "Walk forward 2 steps, do a small split step (a tiny bounce onto both feet into a ready position), then step out left or right as if moving to a ball. Small and light. Until you pass the hop checklist, keep the bounce on the ground (heels lift, toes stay down).",
      yt("pickleball split step footwork drill"), easier="No bounce: stop in a ready position and step out.")
    L("brake_step", "Forward step and brake", "Footwork",
      "Walk 2 or 3 quick steps forward, then stop within 2 steps in a balanced ready position, knees bent and chest up, like arriving at the kitchen line. Hold 2 seconds.",
      yt("deceleration drill forward stop athletic stance"), easier="Slower approach.")
    L("bike_intervals", "Optional bike intervals", "Conditioning",
      "Fayetteville. Assault bike or upright bike: 20 seconds of hard pedaling, then 40 seconds easy. Hard means you couldn't hold a conversation, not an all-out sprint.",
      yt("assault bike intervals beginner"),
      swap="The Villages: a brisk walk with 20 seconds of fast walking every minute, or 20 seconds of quick feet.",
      optional=True, where="Fayetteville")

    L("calf_stretch", "Wall calf stretch, straight then bent knee", "Cool-down",
      "Hands on a wall, one foot back, heel down. Lean in with the back knee straight, then bend the back knee slightly and lean again (that reaches the lower calf).",
      yt("wall calf stretch straight and bent knee"))
    L("hip_front_stretch", "Gentle standing hip-front stretch", "Cool-down",
      "Stand in a short staggered stance holding a counter. Tuck your seat under and shift forward gently until you feel a mild stretch in the front of the back hip. Mild only: no forcing, no lunging.",
      yt("standing hip flexor stretch gentle"), easier="Shorter stance, less shift.")
    L("forearm_stretch", "Forearm stretch, palm up", "Cool-down",
      "Arm straight in front, palm up. With the other hand, gently pull the fingers down and back until you feel a mild stretch in the inner forearm.",
      yt("wrist flexor stretch golfers elbow"))
    L("doorway_stretch", "Doorway chest stretch", "Cool-down",
      "Forearm on a door frame, elbow at shoulder height. Step through gently until you feel a stretch across the front of the chest and shoulder.",
      yt("doorway pec stretch"))

    L("test_calf", "Test: calf raise count, each leg", "Retest",
      "Single leg, fingertips on a wall, flat floor. Count full-height raises at a steady pace (about 2 seconds up, 2 down) until you can't reach full height or your form breaks. Record both, for example 'R 22, L 27'. Goal: right within 90 percent of left, and 25 or more each side.",
      yt("single leg heel raise test"))
    L("test_chair", "Test: 30-second sit-to-stand", "Retest",
      "Bench at knee height, arms crossed on your chest. Count how many times you stand up fully and sit back down in 30 seconds. A standard test for adults 50 and up.",
      yt("30 second chair stand test"), easier="Use your hands, and note that you did.")
    L("test_balance", "Test: single-leg balance", "Retest",
      "Each leg, next to a counter: time how long you can stand on one leg with eyes open (stop at 60 seconds), then eyes closed (stop at 20 seconds).",
      yt("single leg stance test"))
    L("test_side_plank", "Test: side plank hold", "Retest",
      "Side plank on whichever version you've been training (knees or feet). Time each side, up to 60 seconds, stopping when your hips sag.",
      yt("side plank test"))
    L("test_grip", "Test: farmer hold time", "Retest",
      "Two 30 lb dumbbells (two 50s from the strength phase on). Time how long you can hold them standing tall, up to 90 seconds. Note which weight you used.",
      yt("farmer hold test"))
    L("test_hang", "Test: hang or pulldown hold", "Retest",
      "Fayetteville: time a full dead hang (feet off) up to 60 seconds, and count strict pull-ups if you like. The Villages: time the band pulldown hold up to 60 seconds. Record which one you did.",
      yt("dead hang test"), optional=True)
    L("test_elbow", "Test: elbow and shoulder check", "Retest",
      "Palm-up wrist hold with 15 lb for 30 seconds, right arm: record inner-elbow pain 0 to 10. Then 10 band outward rotations with the arm out to the side: record shoulder pain 0 to 10. Both should be 0 to 2.",
      yt("isometric wrist flexion hold"))
