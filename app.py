#!/usr/bin/env python3
import os

import aws_cdk as cdk

from vacation_tracker_cdk.vacation_tracker_cdk_stack import VacationTrackerCdkStack


app = cdk.App()
VacationTrackerCdkStack(app, "VacationTrackerCdkStack")

app.synth()
