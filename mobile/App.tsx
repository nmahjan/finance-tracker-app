import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from './store/authStore';
import { initializeAPI } from './services/api';

// Screens
import LoginScreen from './screens/auth/LoginScreen';
import RegisterScreen from './screens/auth/RegisterScreen';
import DashboardScreen from './screens/dashboard/DashboardScreen';
import TransactionsScreen from './screens/transactions/TransactionsScreen';
import BudgetsScreen from './screens/budgets/BudgetsScreen';
import BillsScreen from './screens/bills/BillsScreen';
import AnalyticsScreen from './screens/analytics/AnalyticsScreen';
import ProfileScreen from './screens/profile/ProfileScreen';
import BankLinkScreen from './screens/plaid/BankLinkScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Auth Stack
function AuthStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: false }} />
    </Stack.Navigator>
  );
}

// App Stack (Authenticated)
function AppTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#ccc',
        headerStyle: { backgroundColor: '#f8f8f8' },
        headerTitleStyle: { fontSize: 18, fontWeight: '600' }
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color }) => <DashboardIcon color={color} />
        }}
      />
      <Tab.Screen
        name="Transactions"
        component={TransactionsScreen}
        options={{
          tabBarLabel: 'Transactions',
          tabBarIcon: ({ color }) => <TransactionsIcon color={color} />
        }}
      />
      <Tab.Screen
        name="Budgets"
        component={BudgetsScreen}
        options={{
          tabBarLabel: 'Budgets',
          tabBarIcon: ({ color }) => <BudgetsIcon color={color} />
        }}
      />
      <Tab.Screen
        name="Bills"
        component={BillsScreen}
        options={{
          tabBarLabel: 'Bills',
          tabBarIcon: ({ color }) => <BillsIcon color={color} />
        }}
      />
      <Tab.Screen
        name="Analytics"
        component={AnalyticsScreen}
        options={{
          tabBarLabel: 'Analytics',
          tabBarIcon: ({ color }) => <AnalyticsIcon color={color} />
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color }) => <ProfileIcon color={color} />
        }}
      />
    </Tab.Navigator>
  );
}

// Placeholder icons (in real app, use expo-vector-icons)
const DashboardIcon = ({ color }) => null;
const TransactionsIcon = ({ color }) => null;
const BudgetsIcon = ({ color }) => null;
const BillsIcon = ({ color }) => null;
const AnalyticsIcon = ({ color }) => null;
const ProfileIcon = ({ color }) => null;

export default function App() {
  const isAuthed = useAuthStore((state) => state.isAuthed);
  const initAuth = useAuthStore((state) => state.initAuth);

  useEffect(() => {
    initAuth();
    initializeAPI();
  }, []);

  return (
    <NavigationContainer>
      {isAuthed ? <AppTabs /> : <AuthStack />}
    </NavigationContainer>
  );
}
