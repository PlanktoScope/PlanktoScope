import { Pressable, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";

import { ItemData } from "./Select";

type ItemProps = {
  item: ItemData;
  onPress: () => void;
  selected?: boolean;
};

export const ITEM_HEIGHT = 52;

export default function SelectItem({
  item,
  onPress,
  selected = false,
}: ItemProps) {
  return (
    <Pressable onPress={onPress}>
      <View
        style={{
          flexDirection: "row",
          minHeight: ITEM_HEIGHT,
          height: ITEM_HEIGHT,
          maxHeight: ITEM_HEIGHT,
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: "lightgrey",
        }}
      >
        <Ionicons
          name="checkmark"
          size={24}
          color="black"
          style={{ opacity: selected ? 1 : 0, paddingRight: 4 }}
        />
        <Text style={{ fontSize: 22 }}>{item.label}</Text>
      </View>
    </Pressable>
  );
}
