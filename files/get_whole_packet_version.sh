# apt-get install jq
version=$(jq -r '.Package' /unitree/robot/pkg/version/version.json)
echo $version
