#!/bin/bash
echo "Manually launching AWS EC2 Instance"
ssh -i NewKeyPair.pem ubuntu@$1
