#!/bin/bash
echo "Manually launching AWS EC2 Instance"
ssh -i ~/keys/NewKeyPair.pem ubuntu@$1
