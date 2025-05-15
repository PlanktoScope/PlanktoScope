import { useCallback, useEffect, useRef, useState } from "react";
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  FlatList,
  StatusBar,
  View,
  TextInput,
} from "react-native";

export type ItemData = {
  value: string;
  label: string;
};

type ItemProps = {
  item: ItemData;
  onPress: () => void;
  selected?: boolean;
};

function Item({ item, onPress, selected = false }: ItemProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.item, selected && styles.itemSelected]}
    >
      <Text style={[styles.title]}>{item.label}</Text>
    </TouchableOpacity>
  );
}

type SelectProps = {
  data: ItemData[];
  selectedValue?: string;
  onSelectedValue?: (value: string) => void;
  search?: boolean;
};

const ITEM_HEIGHT = 52;

export default function Select({
  data,
  selectedValue,
  onSelectedValue,
  search = true,
}: SelectProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const ref = useRef<FlatList>(null);

  const filteredData = !searchTerm
    ? data
    : data.filter((item) => {
        return item.label
          .toLocaleLowerCase()
          .includes(searchTerm.toLocaleLowerCase());
      });

  useEffect(() => {
    if (!selectedValue) return;
    const index = filteredData.findIndex((item) => {
      return item.value === selectedValue;
    });
    if (index < 0) return;

    ref.current?.scrollToIndex({ index, animated: false, viewPosition: 0.5 });
  }, [selectedValue, filteredData]);

  function onSearch(text: string) {
    setSearchTerm(text);
  }

  useEffect(() => {
    ref.current?.scrollToOffset({
      offset: 0,
      animated: false,
    });
  }, [searchTerm]);

  const renderItem = useCallback(
    function renderItem({ item }: { item: ItemData }) {
      return (
        <Item
          item={item}
          onPress={() => onSelectedValue?.(item.value)}
          selected={item.value === selectedValue}
        />
      );
    },
    [onSelectedValue, selectedValue]
  );

  return (
    <View style={styles.container}>
      {search && (
        <TextInput
          style={styles.search}
          placeholder="Search"
          value={searchTerm}
          onChangeText={onSearch}
        />
      )}

      <FlatList
        ref={ref}
        data={filteredData}
        renderItem={renderItem}
        keyExtractor={(item) => item.value}
        extraData={data}
        getItemLayout={(data, index) => ({
          length: ITEM_HEIGHT,
          offset: ITEM_HEIGHT * index,
          index,
        })}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginTop: StatusBar.currentHeight || 0,
  },
  item: {
    minHeight: ITEM_HEIGHT,
    height: ITEM_HEIGHT,
    maxHeight: ITEM_HEIGHT,
  },
  itemSelected: {
    backgroundColor: "pink",
  },
  search: {
    height: 40,
    margin: 12,
    borderWidth: 1,
    padding: 10,
  },
  title: {
    fontSize: 24,
  },
});
