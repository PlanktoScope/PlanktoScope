import { Text, View, Button } from "react-native";

import { useRouter } from "expo-router";

export default function Setup() {
  const { navigate } = useRouter();

  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        gap: 20,
      }}
    >
      <Text
        style={{ fontSize: 34, textAlign: "center" }}
      >{`Welcome to your\nPlanktoScope!`}</Text>

      <Text>We need to set things up, it will be quick.</Text>

      <Button title="Let's start" onPress={() => navigate("/setup/hardware")} />
    </View>
  );
}
