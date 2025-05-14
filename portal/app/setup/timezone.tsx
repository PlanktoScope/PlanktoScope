import { View, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

import timezones from "timezones-list";

import Select, { ItemData } from "../../components/Select";
import useRemoteValue from "@/hooks/useRemoteValue";

export default function WizardTimezone() {
  const { navigate } = useRouter();
  const [timezone, submitValue] = useRemoteValue(
    "http://localhost:8585/timezone"
  );

  function onSelectedValue(value: string) {
    submitValue(value).then(() => {
      navigate("/");
    });
  }

  return (
    <View style={styles.view}>
      <Select
        data={TIMEZONES}
        selectedValue={timezone}
        onSelectedValue={onSelectedValue}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  view: {
    flex: 1,
  },
});

// Use timedatectl list-timezones
// TODO: Detect browser
const TIMEZONES: ItemData[] = timezones
  .map((item) => {
    return { label: item.label, value: item.tzCode };
  })
  .sort((a, b) => {
    return a.label.localeCompare(b.label);
  });
