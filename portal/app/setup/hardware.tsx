import { View, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

import Select, { ItemData } from "../../components/Select";
import useRemoteValue from "@/hooks/useRemoteValue";
import { useEffect, useState } from "react";
import fetch from "@/fetch";

export default function Hardware() {
  const { navigate } = useRouter();
  const [hardware, submitValue] = useRemoteValue("/hardware");
  const [hardwareVersions, setHardwareVersions] = useState([]);

  function onSelectedValue(value: string) {
    submitValue(value).then(() => {
      navigate("/setup/country");
    });
  }

  useEffect(() => {
    getHardwareVersions().then(setHardwareVersions);
  }, []);

  console.log(hardware);

  return (
    <View style={styles.view}>
      <Select
        data={hardwareVersions}
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

async function getHardwareVersions() {
  const res = await fetch("/hardware-versions");
  return res.json();
}
