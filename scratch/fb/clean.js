const { initializeApp } = require('firebase/app');
const { getFirestore, collection, getDocs, deleteDoc, doc } = require('firebase/firestore/lite');

const firebaseConfig = {
  apiKey: "AIzaSyDZE65pb7oiBc6oa8NbTlHPf1QB55I9RXA",
  authDomain: "gym-notebook-74450.firebaseapp.com",
  projectId: "gym-notebook-74450",
  storageBucket: "gym-notebook-74450.firebasestorage.app",
  messagingSenderId: "980458996682",
  appId: "1:980458996682:web:4d80b560fd8a9f65c78533"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function clean() {
  const usersCol = collection(db, 'users');
  const userSnap = await getDocs(usersCol);
  
  let deletedCount = 0;
  
  for (const userDoc of userSnap.docs) {
    const data = userDoc.data();
    const name = data?.settings?.userName || '';
    
    if (name.toLowerCase().includes('miles')) {
      console.log('Keeping user:', userDoc.id, name);
      continue;
    }
    
    console.log('Deleting user:', userDoc.id, name);
    
    // Attempt to delete 'data' subcollection
    try {
        const dataCol = collection(db, `users/${userDoc.id}/data`);
        const dataSnap = await getDocs(dataCol);
        for(const dDoc of dataSnap.docs) {
            await deleteDoc(doc(db, `users/${userDoc.id}/data/${dDoc.id}`));
        }
    } catch(e) {}
    
    // Delete user doc
    await deleteDoc(doc(db, 'users', userDoc.id));
    deletedCount++;
  }
  
  console.log(`Deleted ${deletedCount} users.`);
}

clean().then(() => console.log('Done')).catch(console.error);
