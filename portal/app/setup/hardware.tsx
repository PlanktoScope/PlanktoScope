import { View, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

import Select, { ItemData } from "../../components/Select";
import useRemoteValue from "@/hooks/useRemoteValue";

export default function Hardware() {
  const { navigate } = useRouter();
  const [hardware, submitValue] = useRemoteValue(
    "http://localhost:8585/hardware"
  );

  function onSelectedValue(value: string) {
    submitValue(value).then(() => {
      navigate("/setup/country");
    });
  }

  return (
    <View style={styles.view}>
      <Select
        data={HARDWARE_VERSIONS}
        selectedValue={hardware}
        onSelectedValue={onSelectedValue}
        search={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  view: {
    flex: 1,
  },
});

// Fetch from backend
const HARDWARE_VERSIONS: ItemData[] = [
  "v3.0",
  "v2.6",
  "v2.5",
  "v2.3",
  "v2.1",
].map((v) => {
  return { label: `PlanktoScope ${v}`, value: `PlanktoScope ${v}` };
});
