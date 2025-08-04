import os
import shutil

from src.GetBPObs import calculate_bp_obs
from src.GetCalculatedEnergyObs import calculate_energy_obs
from src.GetDemographics import calculate_demographics
from src.GetEnteralFeedObs import calculate_entral_feed_obs
from src.GetHeadCircumObs import calculate_head_circum_obs
from src.GetHeightObs import calculate_height_obs
from src.GetPulseObs import calculate_pulse_obs
from src.GetRespObs import calculate_resp_obs
from src.GetSPO2 import calculate_spo2_obs
from src.GetStoolWeight import calculate_stool_obs
from src.GetWeightObs import calculate_weight_obs
from src.GetFluids import calculate_fluids

os.chdir("/home/walkerdavis/projects/mpsc")
patientJSONDir = "./data/raw"
output_dir = "./data/processed"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

os.makedirs(output_dir)

with open("resources/FluidIntakeRowIDs.txt", "r") as fluidIntakeRowIDsFile:
    fluidIntakeRowIDs = fluidIntakeRowIDsFile.read().splitlines()

with open("resources/FluidOutputRowIDs.txt", "r") as fluidOutputRowIDsFile:
    fluidOutputRowIDs = fluidOutputRowIDsFile.read().splitlines()

calculate_fluids(patientJSONDir, output_dir, fluidIntakeRowIDs, fluidOutputRowIDs)
calculate_weight_obs(patientJSONDir, output_dir)
calculate_height_obs(patientJSONDir, output_dir)
calculate_head_circum_obs(patientJSONDir, output_dir)
calculate_entral_feed_obs(patientJSONDir, output_dir)
calculate_demographics(patientJSONDir, fluidIntakeRowIDs, output_dir)
calculate_energy_obs(patientJSONDir, output_dir)
calculate_bp_obs(patientJSONDir, output_dir)
calculate_spo2_obs(patientJSONDir, output_dir)
calculate_resp_obs(patientJSONDir, output_dir)
calculate_stool_obs(patientJSONDir, output_dir)
calculate_pulse_obs(patientJSONDir, output_dir)
