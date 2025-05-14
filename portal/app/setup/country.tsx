import { StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import { iso31661 } from "iso-3166";

import Select, { ItemData } from "../../components/Select";
import useRemoteValue from "@/hooks/useRemoteValue";

export default function Country() {
  const { navigate } = useRouter();
  const [country, submitValue] = useRemoteValue(
    "http://localhost:8585/country"
  );

  function onSelectedValue(value: string) {
    submitValue(value).then(() => {
      navigate("/setup/timezone");
    });
  }

  return (
    <View style={styles.view}>
      <Select
        data={COUNTRIES}
        selectedValue={country}
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

// Use /usr/share/zoneinfo/iso3166.tab
// TODO: Detect browser/ip
const COUNTRIES: ItemData[] = iso31661
  .map((item) => {
    return { label: item.name, value: item.alpha2 };
  })
  .sort((a, b) => {
    return a.label.localeCompare(b.label);
  });
