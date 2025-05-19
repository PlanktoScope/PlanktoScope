import { useFonts } from "expo-font";
import { Stack } from "expo-router";
import Head from "expo-router/head";
import { StatusBar } from "expo-status-bar";
import { Platform } from "react-native";

export default function RootLayout() {
  const [loaded] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
  });

  if (!loaded) {
    // Async font loading only occurs in development.
    return null;
  }

  return (
    <>
      {/* https://github.com/expo/router/discussions/267 */}
      {Platform.OS === "web" && (
        <Head>
          <title>PlanktoScope</title>
        </Head>
      )}
      <Stack>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen
          name="setup/index"
          options={{ headerShown: true, title: "Welcome!" }}
        />
        <Stack.Screen name="setup/hardware" options={{ title: "Hardware" }} />
        <Stack.Screen name="setup/country" options={{ title: "Country" }} />
        <Stack.Screen name="setup/timezone" options={{ title: "Timezone" }} />
        <Stack.Screen name="+not-found" />
      </Stack>
      <StatusBar style="auto" />
    </>
  );
}
