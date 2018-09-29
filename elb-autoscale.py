#!/usr/bin/python

import boto3
import subprocess
import time

elb = boto3.client('elbv2')

create_elb = elb.create_load_balancer(

		Name='scale-elb',
		Type='network',
		Scheme='internet-facing',
		Subnets=[
		"subnet-23b9f369",
		"subnet-9860e1b6",
		"subnet-d47dc7b3",
		"subnet-5e76f102",
		"subnet-5099e55f",
		"subnet-f75799c9" ],
		IpAddressType='ipv4'    )


target_group = elb.create_target_group(
		
		Name='scale-target',
		Protocol='TCP',
		Port=80,
		VpcId="vpc-fec81e84",
		
		)

loadstring = subprocess.check_output("aws elbv2 describe-load-balancers --names scale-elb --query LoadBalancers[*].LoadBalancerArn --output text", shell=True ).strip()
tgarn = subprocess.check_output("aws elbv2 describe-target-groups --name scale-target --query TargetGroups[*].[TargetGroupArn] --output text", shell=True).strip() 

listener = elb.create_listener(

		LoadBalancerArn=loadstring,
		Protocol='TCP',
		Port=80,
		DefaultActions=[
			{
				'Type': 'forward',
				'TargetGroupArn': tgarn,
			}
		]
							)


autoscaling = boto3.client('autoscaling')


launchconfig = autoscaling.create_launch_configuration(

		LaunchConfigurationName='autoscaling-launch-config1',
		ImageId='ami-06413385decaa839a',
		InstanceType='t2.micro',
		KeyName='py-key-pair',
		SecurityGroups=['sg-066b3a583b1bb9687']
		
		)

time.sleep(10)

create_group = autoscaling.create_auto_scaling_group(

		LaunchConfigurationName='autoscaling-launch-config1',
		AutoScalingGroupName='testscale-group',
		MinSize=2,
		MaxSize=4,
		DesiredCapacity=2,
		AvailabilityZones=['us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f'],
		TargetGroupARNs=[tgarn]

	)	


attach_target_group = autoscaling.attach_load_balancer_target_groups(

		AutoScalingGroupName='testscale-group',
		TargetGroupARNs=[tgarn]

		)











	
