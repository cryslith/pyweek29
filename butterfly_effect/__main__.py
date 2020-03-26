import argparse

import ppb

import butterfly_effect as be


parser = argparse.ArgumentParser(description="Dev tooling to choose scene to start.")
parser.add_argument("-s", dest="start_scene")
args = parser.parse_args()

run_first = be.scene_map.get(args.start_scene, be.Splash)

ppb.run(starting_scene=run_first, systems=be.systems)
