# Notes

- Calculated Energy will need its own parser to handle TreatmentRoute
- Need to add demographics and fluids
- For stool weight, aggregate over a single day / week as a sum
- Calories in - calories used for maintenence = calories for growth
- Add feature to tell the model which growth phase the child is in

- instead of predicting growth, determine whether growth has failed.
    - figure out how to define growth failure
    - smoothing over 2 weeks will likely remove deviations without falling out of critical phase
    - what is the z score change likely to be over the next period?

- Be very diligent with leaking future features. For use in clinical trials, model should input data regarding patient up to the present. Medicine orders can go up to the present + 1 day.