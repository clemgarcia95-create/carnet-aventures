import { useEffect, useState, FormEvent } from 'react';
import { supabase } from './lib/supabase';
import { motion, AnimatePresence } from 'motion/react';
import confetti from 'canvas-confetti';
import { Heart, Plane, Utensils, Home, PartyPopper, Sparkles, Check, Trash2, Plus, X, Lock, Image as ImageIcon } from 'lucide-react';

interface Aventure {
  id: number;
  titre: string;
  categorie: string;
  auteur: string;
  statut_fait: boolean;
  note_souvenir: string | null;
  date_creation: string;
}

const CATEGORIES = [
  { name: "Voyage ✈️", icon: Plane },
  { name: "Food 🍕", icon: Utensils },
  { name: "Maison 🏠", icon: Home },
  { name: "Sorties 🎭", icon: PartyPopper },
  { name: "Folie 🤪", icon: Sparkles },
];

const AUTEURS = ["Joanna 🌸", "Clément 🦊"];

export default function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState(false);

  const [data, setData] = useState<Aventure[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'envies' | 'souvenirs'>('envies');

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [itemToComplete, setItemToComplete] = useState<Aventure | null>(null);
  const [itemToDelete, setItemToDelete] = useState<Aventure | null>(null);

  // Form state
  const [newTitre, setNewTitre] = useState('');
  const [newCat, setNewCat] = useState(CATEGORIES[0].name);
  const [newAuteur, setNewAuteur] = useState(AUTEURS[0]);
  const [note, setNote] = useState('');

  useEffect(() => {
    if (authenticated) {
      fetchData();
    }
  }, [authenticated]);

  const fetchData = async () => {
    setLoading(true);
    const { data: aventures, error } = await supabase
      .from('carnet_aventures')
      .select('*')
      .order('date_creation', { ascending: false });

    if (!error && aventures) {
      setData(aventures);
    }
    setLoading(false);
  };

  const handleLogin = (e: FormEvent) => {
    e.preventDefault();
    if (password === 'Amour') {
      setAuthenticated(true);
      setPasswordError(false);
    } else {
      setPasswordError(true);
    }
  };

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTitre.trim()) return;

    const { error } = await supabase.from('carnet_aventures').insert({
      titre: newTitre,
      categorie: newCat,
      auteur: newAuteur,
      statut_fait: false,
    });

    if (!error) {
      setNewTitre('');
      setIsAddModalOpen(false);
      fetchData();
    }
  };

  const handleComplete = async () => {
    if (!itemToComplete) return;

    const { error } = await supabase
      .from('carnet_aventures')
      .update({
        statut_fait: true,
        note_souvenir: note,
      })
      .eq('id', itemToComplete.id);

    if (!error) {
      setItemToComplete(null);
      setNote('');
      fetchData();
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3']
      });
    }
  };

  const handleDelete = async () => {
    if (!itemToDelete) return;

    const { error } = await supabase
      .from('carnet_aventures')
      .delete()
      .eq('id', itemToDelete.id);

    if (!error) {
      setItemToDelete(null);
      fetchData();
    }
  };

  const triggerSurprise = () => {
    const envies = data.filter(d => !d.statut_fait);
    if (envies.length === 0) return;
    
    const choix = envies[Math.floor(Math.random() * envies.length)];
    confetti({
      particleCount: 150,
      spread: 100,
      origin: { y: 0.5 },
      colors: ['#ff9ff3', '#feca57', '#ff6b6b']
    });
    alert(`L'aventure du jour : ${choix.titre} !`);
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-8 rounded-3xl shadow-xl max-w-md w-full border border-pink-100"
        >
          <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Lock className="w-8 h-8 text-pink-500" />
          </div>
          <h1 className="text-2xl font-bold text-center text-gray-800 mb-2">Accès Privé</h1>
          <p className="text-center text-gray-500 mb-8">Entrez le mot de passe pour accéder à votre carnet.</p>
          
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mot de passe secret..."
                className={`w-full px-4 py-3 rounded-xl border ${passwordError ? 'border-red-300 bg-red-50' : 'border-gray-200'} focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all`}
              />
              {passwordError && <p className="text-red-500 text-sm mt-2">Mot de passe incorrect ❌</p>}
            </div>
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold py-3 rounded-xl hover:opacity-90 transition-opacity shadow-md shadow-pink-500/30"
            >
              Se connecter
            </button>
          </form>
        </motion.div>
      </div>
    );
  }

  const envies = data.filter(d => !d.statut_fait);
  const souvenirs = data.filter(d => d.statut_fait);
  const progress = data.length > 0 ? (souvenirs.length / data.length) * 100 : 0;

  return (
    <div className="min-h-screen pb-24">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md sticky top-0 z-30 border-b border-pink-100 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <h1 className="text-3xl md:text-4xl font-bold text-center text-gray-800 flex items-center justify-center gap-3">
            <Heart className="text-pink-500 fill-pink-500" />
            Notre Carnet d'Aventures
            <Heart className="text-pink-500 fill-pink-500" />
          </h1>
          
          {/* Progress Bar */}
          <div className="mt-6 max-w-2xl mx-auto">
            <div className="flex justify-between text-sm font-medium text-gray-600 mb-2">
              <span>Nos rêves réalisés</span>
              <span>{souvenirs.length} / {data.length} ({Math.round(progress)}%) ✨</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-pink-400 to-rose-500"
              />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex justify-center mb-10">
          <div className="bg-white p-1 rounded-2xl shadow-sm border border-gray-100 inline-flex">
            <button
              onClick={() => setActiveTab('envies')}
              className={`px-6 py-2.5 rounded-xl font-medium transition-all ${
                activeTab === 'envies' 
                  ? 'bg-pink-50 text-pink-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              🎯 Nos Envies
            </button>
            <button
              onClick={() => setActiveTab('souvenirs')}
              className={`px-6 py-2.5 rounded-xl font-medium transition-all ${
                activeTab === 'souvenirs' 
                  ? 'bg-pink-50 text-pink-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              📸 Nos Souvenirs
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-pink-200 border-t-pink-500"></div>
          </div>
        ) : (
          <AnimatePresence mode="wait">
            {activeTab === 'envies' ? (
              <motion.div
                key="envies"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {/* Actions Bar */}
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-8">
                  <button
                    onClick={() => setIsAddModalOpen(true)}
                    className="w-full sm:w-auto flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 px-6 py-3 rounded-2xl hover:bg-gray-50 hover:border-gray-300 transition-all font-medium shadow-sm"
                  >
                    <Plus className="w-5 h-5" />
                    Ajouter une nouvelle envie
                  </button>
                  
                  {envies.length > 0 && (
                    <button
                      onClick={triggerSurprise}
                      className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-6 py-3 rounded-2xl hover:opacity-90 transition-all font-medium shadow-md shadow-indigo-500/20"
                    >
                      🎲 Surprise-nous !
                    </button>
                  )}
                </div>

                {envies.length === 0 ? (
                  <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-gray-300">
                    <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-medium text-gray-600 mb-2">La liste est vide ! 🚀</h3>
                    <p className="text-gray-400">Ajoutez votre première aventure à vivre ensemble.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {envies.map((item) => (
                      <motion.div
                        layout
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        key={item.id}
                        className="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-shadow flex flex-col group"
                      >
                        <div className="relative aspect-[4/3] bg-gray-100 overflow-hidden">
                          <img 
                            src={`https://image.pollinations.ai/prompt/${encodeURIComponent(item.titre)}`}
                            alt={item.titre}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                            loading="lazy"
                          />
                          <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium text-gray-700 shadow-sm">
                            {item.categorie}
                          </div>
                        </div>
                        
                        <div className="p-5 flex-1 flex flex-col">
                          <h3 className="text-lg font-bold text-gray-800 mb-1">{item.titre}</h3>
                          <p className="text-sm text-gray-500 mb-4">Proposé par {item.auteur}</p>
                          
                          <div className="mt-auto flex gap-2 pt-4 border-t border-gray-50">
                            <button
                              onClick={() => setItemToComplete(item)}
                              className="flex-1 flex items-center justify-center gap-2 bg-green-50 text-green-600 py-2.5 rounded-xl font-medium hover:bg-green-100 transition-colors"
                            >
                              <Check className="w-4 h-4" />
                              Fait !
                            </button>
                            <button
                              onClick={() => setItemToDelete(item)}
                              className="w-11 flex items-center justify-center bg-red-50 text-red-500 rounded-xl hover:bg-red-100 transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="souvenirs"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {souvenirs.length === 0 ? (
                  <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-gray-300">
                    <ImageIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-medium text-gray-600 mb-2">Pas encore de souvenirs... 🏃‍♂️</h3>
                    <p className="text-gray-400">Réalisez vos envies pour remplir ce mur !</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 px-4">
                    {souvenirs.map((item, index) => (
                      <motion.div
                        initial={{ opacity: 0, rotate: Math.random() * 10 - 5 }}
                        animate={{ opacity: 1, rotate: index % 2 === 0 ? -2 : 2 }}
                        whileHover={{ scale: 1.05, rotate: 0, zIndex: 10 }}
                        key={item.id}
                        className="bg-white p-4 pb-12 shadow-xl rounded-sm border border-gray-200 flex flex-col relative group"
                      >
                        <div className="aspect-square bg-gray-100 overflow-hidden mb-4">
                          <img 
                            src={`https://image.pollinations.ai/prompt/${encodeURIComponent(item.titre + " photography")}`}
                            alt={item.titre}
                            className="w-full h-full object-cover"
                            loading="lazy"
                          />
                        </div>
                        
                        <div className="text-center">
                          <h3 className="font-handwriting text-2xl font-bold text-gray-800">{item.titre}</h3>
                          {item.note_souvenir && (
                            <p className="font-handwriting text-xl text-gray-600 mt-2 leading-tight">
                              « {item.note_souvenir} »
                            </p>
                          )}
                        </div>

                        <button
                          onClick={() => setItemToDelete(item)}
                          className="absolute bottom-3 right-3 p-2 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </motion.div>
                    ))}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </main>

      {/* Add Modal */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden"
            >
              <div className="flex justify-between items-center p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-800">Ajouter une envie ✨</h2>
                <button onClick={() => setIsAddModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <form onSubmit={handleAdd} className="p-6 space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Qu'est-ce qui te ferait plaisir ?</label>
                  <input
                    type="text"
                    required
                    value={newTitre}
                    onChange={(e) => setNewTitre(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                    placeholder="Ex: Week-end à Rome..."
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
                    <select
                      value={newCat}
                      onChange={(e) => setNewCat(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-pink-500 outline-none bg-white"
                    >
                      {CATEGORIES.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Proposé par</label>
                    <select
                      value={newAuteur}
                      onChange={(e) => setNewAuteur(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-pink-500 outline-none bg-white"
                    >
                      {AUTEURS.map(a => <option key={a} value={a}>{a}</option>)}
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-gray-900 text-white font-semibold py-3.5 rounded-xl hover:bg-gray-800 transition-colors mt-2"
                >
                  Ajouter à notre liste
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Complete Modal */}
      <AnimatePresence>
        {itemToComplete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden p-6 text-center"
            >
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-green-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Bravo ! 📸</h2>
              <p className="text-gray-600 mb-6">Vous avez réalisé : <strong className="text-gray-900">{itemToComplete.titre}</strong></p>
              
              <div className="text-left mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Un petit mot sur ce moment ? (Optionnel)</label>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-green-500 outline-none transition-all resize-none h-24"
                  placeholder="C'était incroyable parce que..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setItemToComplete(null);
                    setNote('');
                  }}
                  className="flex-1 px-4 py-3 rounded-xl font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleComplete}
                  className="flex-1 px-4 py-3 rounded-xl font-medium text-white bg-green-500 hover:bg-green-600 transition-colors shadow-md shadow-green-500/20"
                >
                  Confirmer ✅
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Delete Modal */}
      <AnimatePresence>
        {itemToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden p-6 text-center"
            >
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Trash2 className="w-8 h-8 text-red-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Supprimer l'élément ?</h2>
              <p className="text-gray-600 mb-6">Veux-tu vraiment supprimer <strong className="text-gray-900">{itemToDelete.titre}</strong> ? Cette action est irréversible.</p>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setItemToDelete(null)}
                  className="flex-1 px-4 py-3 rounded-xl font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleDelete}
                  className="flex-1 px-4 py-3 rounded-xl font-medium text-white bg-red-500 hover:bg-red-600 transition-colors shadow-md shadow-red-500/20"
                >
                  Oui, supprimer
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

