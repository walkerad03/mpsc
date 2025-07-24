import os
import shutil

from GetWeightObs import calculate_weight_obs
from GetHeightObs import calculate_height_obs
from GetHeadCircumObs import calculate_head_circum_obs
from GetEnteralFeedObs import calculate_entral_feed_obs
from GetDemographics import calculate_demographics
from GetCalculatedEnergyObs import calculate_energy_obs

os.chdir("/home/walkerdavis/projects/mpsc")
patientJSONDir = "./data/raw"
output_dir = "./data/processed"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

os.makedirs(output_dir)

with open("scripts/FluidIntakeRowIDs.txt", "r") as fluidIntakeRowIDsFile:
    fluidIntakeRowIDs = fluidIntakeRowIDsFile.read().splitlines()

calculate_weight_obs(patientJSONDir, output_dir)
calculate_height_obs(patientJSONDir, output_dir)
calculate_head_circum_obs(patientJSONDir, output_dir)
calculate_entral_feed_obs(patientJSONDir, output_dir)
calculate_demographics(patientJSONDir, fluidIntakeRowIDs, output_dir)
calculate_energy_obs(patientJSONDir, output_dir)
