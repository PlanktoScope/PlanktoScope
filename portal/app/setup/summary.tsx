import { View, StyleSheet, Text } from "react-native";
import { useRouter } from "expo-router";

export default function Summary({ config }) {
  const { navigate } = useRouter();

  function onSelectedValue(value: string) {
    console.log(value);
    navigate("/setup/country");
  }

  return (
    <View style={styles.view}>
      <Text>{config.hardware}</Text>
      <Text>{config.country}</Text>
      <Text>{config.timezone}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  view: {
    flex: 1,
  },
});
