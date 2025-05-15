import { View, Text } from "react-native";

export default function NotFoundScreen() {
  return (
    <View
      style={{
        flex: 1,
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <Text style={{ fontSize: 24 }}>Congrratulations.</Text>
    </View>
  );
}
