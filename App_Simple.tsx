import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';

export default function App() {
  const [message, setMessage] = React.useState('Navigation Assistant');

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>{message}</Text>

        <Text style={styles.subtitle}>
          Camera-based navigation for visually impaired users
        </Text>

        <TouchableOpacity
          style={styles.button}
          onPress={() =>
            setMessage('App is working! Camera integration coming soon...')
          }
        >
          <Text style={styles.buttonText}>Test App</Text>
        </TouchableOpacity>

        <Text style={styles.info}>
          This is a test build.{'\n'}
          Full features will be added after confirming the app works.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#aaa',
    marginBottom: 40,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#0f3460',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 25,
    marginBottom: 30,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  info: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginTop: 20,
  },
});
