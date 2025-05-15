import { StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";

import Select, { ItemData } from "../../components/Select";
import useRemoteValue from "@/hooks/useRemoteValue";
import { useEffect, useState } from "react";
import fetch from "@/fetch";

export default function Country() {
  const { navigate } = useRouter();
  const [country, submitValue] = useRemoteValue("/country");
  const [countries, setCountries] = useState([]);

  function onSelectedValue(value: string) {
    submitValue(value).then(() => {
      navigate("/setup/timezone");
    });
  }

  useEffect(() => {
    getCountries().then(setCountries);
  }, []);

  return (
    <View style={styles.view}>
      <Select
        data={countries}
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

// TODO: Detect browser/ip

async function getCountries() {
  const res = await fetch("/countries");
  return res.json();
}
