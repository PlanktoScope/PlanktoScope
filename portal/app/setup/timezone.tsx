import { View, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { useState, useEffect } from "react";

import fetch from "@/fetch";

import Select, { ItemData } from "../../components/Select";
import useRemoteValue from "@/hooks/useRemoteValue";

export default function WizardTimezone() {
  const { navigate } = useRouter();
  const [timezone, submitValue] = useRemoteValue("/timezone");
  const [timezones, setTimezones] = useState([]);

  function onSelectedValue(value: string) {
    submitValue(value).then(() => {
      navigate("/setup/done");
    });
  }

  useEffect(() => {
    getTimezones().then(setTimezones);
  }, []);

  return (
    <View style={styles.view}>
      <Select
        data={timezones}
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

// TODO: Detect browser
async function getTimezones() {
  const res = await fetch("/timezones");
  return res.json();
}
