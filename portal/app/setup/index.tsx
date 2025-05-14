import { Text, View, Button, StyleSheet } from "react-native";

import { ThemedView } from "@/components/ThemedView";

import { useRouter } from "expo-router";

export default function Setup() {
  const { navigate } = useRouter();

  return (
    <ThemedView style={{ flex: 1 }}>
      <View style={styles.view}>
        <Text style={styles.title}>{`Welcome to your\nPlanktoScope!`}</Text>

        <Text>We need to set things up, it will be quick.</Text>

        <Button
          title="Let's start"
          onPress={() => navigate("/setup/hardware")}
        />
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  view: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: 34,
    textAlign: "center",
  },
});
