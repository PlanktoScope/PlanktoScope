import { useFonts } from "expo-font";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import "react-native-reanimated";

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
      <Stack>
        {/* <Stack.Screen name="(tabs)" options={{ headerShown: false }} /> */}
        <Stack.Screen
          name="setup/index"
          options={{ headerShown: false, title: "Welcome!" }}
        />
        <Stack.Screen name="setup/hardware" options={{ title: "Hardware" }} />
        <Stack.Screen name="setup/country" options={{ title: "Country" }} />
        <Stack.Screen name="setup/timezone" options={{ title: "Timezone" }} />
        <Stack.Screen name="setup/done" options={{ title: "Done" }} />
        <Stack.Screen name="+not-found" />
      </Stack>
      <StatusBar style="auto" />
    </>
  );
}
