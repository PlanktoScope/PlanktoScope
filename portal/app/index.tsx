import { Redirect } from "expo-router";
import { useEffect, useState } from "react";
import { View, Text, ScrollView } from "react-native";

import fetch from "@/fetch";
import { HomeText } from "@/components/HomeText";

export default function HomeScreen() {
  const [data, setData] = useState();

  useEffect(() => {
    bootstrap().then(setData);
  }, []);

  if (!data) return null;

  const { name, access_hostname, setup } = data;

  if (setup) {
    return <Redirect href="/setup" />;
  }

  return (
    <ScrollView>
      <HomeText name={name} hostname={access_hostname} />
    </ScrollView>
  );
}

async function bootstrap() {
  const res = await fetch("/bootstrap");
  return await res.json();
}
