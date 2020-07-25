#!/bin/bash
echo "Manually launching AWS EC2 Instance"
ssh -i MyKeyPair.pem ubuntu@$1
