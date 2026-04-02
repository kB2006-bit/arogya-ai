// Symptom History Management using localStorage

const HISTORY_KEY = 'arogya-symptom-history';
const MAX_HISTORY_ITEMS = 50;

export const saveSymptomCheck = (symptomCheck) => {
  try {
    const history = getSymptomHistory();
    const newEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      ...symptomCheck
    };
    
    const updatedHistory = [newEntry, ...history].slice(0, MAX_HISTORY_ITEMS);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
    return newEntry;
  } catch (error) {
    console.error('Failed to save symptom check:', error);
    return null;
  }
};

export const getSymptomHistory = () => {
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load symptom history:', error);
    return [];
  }
};

export const clearSymptomHistory = () => {
  try {
    localStorage.removeItem(HISTORY_KEY);
    return true;
  } catch (error) {
    console.error('Failed to clear symptom history:', error);
    return false;
  }
};

export const deleteSymptomCheck = (id) => {
  try {
    const history = getSymptomHistory();
    const updatedHistory = history.filter(item => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
    return true;
  } catch (error) {
    console.error('Failed to delete symptom check:', error);
    return false;
  }
};

export const getSymptomStats = () => {
  const history = getSymptomHistory();
  return {
    total: history.length,
    high: history.filter(item => item.severity === 'High').length,
    medium: history.filter(item => item.severity === 'Medium').length,
    low: history.filter(item => item.severity === 'Low').length,
  };
};
