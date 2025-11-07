import React, { useState, useEffect, useMemo } from 'react';
import './App.css';
import { BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [selectedLLM, setSelectedLLM] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [selectedEnergy, setSelectedEnergy] = useState('');
  const [prompt, setPrompt] = useState('');
  const [co2Score, setCo2Score] = useState(null);
  const [displayedScore, setDisplayedScore] = useState(0);
  const [energyKwh, setEnergyKwh] = useState(null); // Store energy consumption from API
  const [dropdownOpen, setDropdownOpen] = useState({
    llm: false,
    platform: false,
    energy: false,
  });

  // Data from backend
  const [energyByModelData, setEnergyByModelData] = useState([]);
  const [gpuCpuDistributionData, setGpuCpuDistributionData] = useState([]);
  const [efficiencyData, setEfficiencyData] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [availablePlatforms, setAvailablePlatforms] = useState([]);

  const llmOptions = [
    'alpaca_gemma_2b',
    'alpaca_gemma_7b',
    'alpaca_llama3_70b',
    'alpaca_llama3_8b',
    'codellama_70b',
    'codellama_7b',
    'gemma_2b',
    'gemma_7b'
  ];

  const energyOptions = [
    { name: 'France Mix', value: 'mix_france', co2PerKwh: 32 },
    { name: 'Nuclear', value: 'nuclear', co2PerKwh: 6 },
    { name: 'Wind', value: 'wind', co2PerKwh: 7 },
    { name: 'Solar', value: 'solar', co2PerKwh: 41 },
    { name: 'Hydro', value: 'hydro', co2PerKwh: 6 },
    { name: 'Natural Gas', value: 'gas', co2PerKwh: 490 },
    { name: 'Coal', value: 'coal', co2PerKwh: 820 },
    { name: 'EU Mix', value: 'mix_eu', co2PerKwh: 275 },
  ];

  const platformMapping = {
    'alpaca_gemma_2b': ['laptop', 'workstation'],
    'alpaca_gemma_7b': ['laptop', 'workstation'],
    'alpaca_llama3_70b': ['server'],
    'alpaca_llama3_8b': ['laptop'],
    'codellama_70b': ['workstation'],
    'codellama_7b': ['laptop', 'workstation'],
    'gemma_2b': ['laptop', 'workstation'],
    'gemma_7b': ['laptop', 'workstation']
  };

  const handleLLMSelect = (llm) => {
    setSelectedLLM(llm);
    setSelectedPlatform('');
    setDropdownOpen({ ...dropdownOpen, llm: false });
  };

  const handlePlatformSelect = (platform) => {
    setSelectedPlatform(platform);
    setDropdownOpen({ ...dropdownOpen, platform: false });
  };

  const handleEnergySelect = (energy) => {
    setSelectedEnergy(energy);
    setDropdownOpen({ ...dropdownOpen, energy: false });
    
    // If we already have energy consumption data, recalculate CO2 with new energy source
    if (energyKwh !== null) {
      const energyOption = energyOptions.find(opt => opt.value === energy);
      if (energyOption) {
        const newCo2Grams = energyKwh * energyOption.co2PerKwh;
        const newCo2Mg = newCo2Grams * 1000;
        setCo2Score(newCo2Mg);
      }
    }
  };

  const handleMouseLeave = (dropdownType) => {
    setTimeout(() => {
      setDropdownOpen({ ...dropdownOpen, [dropdownType]: false });
    }, 500);
  };

  const getComparisons = (co2Milligrams) => {
    // Convert mg back to grams for calculations
    const co2Grams = co2Milligrams / 1000;
    
    const smartphoneChargeWh = 5; // 5 Wh per full charge (0% to 100%)
    const treeDayAbsorption = 55; // g CO2 per day (20 kg/year ≈ 55 g/day)
    
    // LED bulb calculation based on energy consumption (kWh from API)
    const ledBulbWh = 10; // 10 Wh per hour (ampoule LED)
    
    // Calculate LED minutes based on energy consumption if available
    let ledMinutes = 0;
    let smartphonePercent = 0;
    
    if (energyKwh !== null) {
      // Convert kWh to Wh (multiply by 1000)
      const energyWh = energyKwh * 1000;
      
      // Calculate hours the LED can be powered, then convert to minutes
      const ledHours = energyWh / ledBulbWh;
      ledMinutes = ledHours * 60;
      
      // Calculate smartphone charges as percentage
      smartphonePercent = (energyWh / smartphoneChargeWh) * 100;
    }
    
    // Calculate tree comparison: convert days to seconds
    // co2Grams / 55 g per day = days needed
    // days * 24 hours * 60 minutes * 60 seconds = seconds
    const treeSeconds = (co2Grams / treeDayAbsorption) * 24 * 60 * 60;
    
    // Format with appropriate precision
    const formatValue = (val) => {
      if (val < 0.001) return val.toExponential(2);
      if (val < 0.01) return val.toFixed(4);
      if (val < 1) return val.toFixed(3);
      if (val < 10) return val.toFixed(2);
      return val.toFixed(1);
    };
    
    return {
      smartphones: formatValue(smartphonePercent),
      ledHours: formatValue(ledMinutes),
      treeDays: formatValue(treeSeconds)
    };
  };

  const handleSubmit = () => {
    if (selectedLLM && selectedPlatform && selectedEnergy && prompt) {
      // Call backend API to calculate real CO2
      fetch(`${API_BASE_URL}/calculate-co2`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedLLM,
          platform: selectedPlatform,
          energy_source: selectedEnergy,
          prompt: prompt
        })
      })
        .then(res => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          console.log('CO2 API response:', data);
          // Store energy consumption for recalculation when energy source changes
          setEnergyKwh(data.energy_kwh);
          // Convert grams to milligrams for display
          setCo2Score(data.co2_grams * 1000);
        })
        .catch(err => {
          console.error('Error calculating CO2:', err);
          alert('❌ Error: Unable to connect to the backend server.\n\nPlease make sure the backend is running on http://localhost:5000\n\nTo start the backend, run:\ncd Code/backend\npython main.py');
        });
    } else {
      alert('Please fill in all fields before submitting');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const handleCloseResults = () => {
    setCo2Score(null);
    setDisplayedScore(0);
    setEnergyKwh(null);
  };

  // Load data from backend on component mount
  useEffect(() => {
    // Fetch energy by model data
    fetch(`${API_BASE_URL}/energy-by-model`)
      .then(res => res.json())
      .then(data => {
        console.log('Energy by model data:', data);
        // Convert kWh to Wh (multiply by 1000) and restructure data
        const restructuredData = data.flatMap(item => {
          const platforms = [];
          if (item.Workstation > 0) {
            platforms.push({
              model: item.model,
              platform: 'Workstation',
              energy: item.Workstation * 1000
            });
          }
          if (item.Server > 0) {
            platforms.push({
              model: item.model,
              platform: 'Server',
              energy: item.Server * 1000
            });
          }
          // Fusionner Laptop1 et Laptop2 en une seule catégorie "Laptop"
          const laptopEnergy = (item.Laptop1 || 0) + (item.Laptop2 || 0);
          if (laptopEnergy > 0) {
            platforms.push({
              model: item.model,
              platform: 'Laptop',
              energy: laptopEnergy * 1000
            });
          }
          return platforms;
        });
        setEnergyByModelData(restructuredData);
      })
      .catch(err => console.error('Error fetching energy-by-model:', err));

    // Fetch GPU vs CPU distribution data
    fetch(`${API_BASE_URL}/gpu-cpu-distribution`)
      .then(res => res.json())
      .then(data => {
        console.log('GPU-CPU distribution data:', data);
        setGpuCpuDistributionData(data);
      })
      .catch(err => console.error('Error fetching GPU-CPU distribution:', err));

    // Fetch efficiency data
    fetch(`${API_BASE_URL}/energy-efficiency`)
      .then(res => res.json())
      .then(data => {
        console.log('Efficiency data:', data);
        // Convert kWh to Wh (multiply by 1000)
        const convertedData = data.map(item => ({
          ...item,
          energy: item.energy * 1000
        }));
        setEfficiencyData(convertedData);
      })
      .catch(err => console.error('Error fetching efficiency:', err));

    // Fetch available models
    fetch(`${API_BASE_URL}/models`)
      .then(res => res.json())
      .then(data => setAvailableModels(data))
      .catch(err => console.error('Error fetching models:', err));
  }, []);

  // Fetch platforms when LLM is selected
  useEffect(() => {
    if (selectedLLM) {
      fetch(`${API_BASE_URL}/platforms/${selectedLLM}`)
        .then(res => res.json())
        .then(data => setAvailablePlatforms(data))
        .catch(err => console.error('Error fetching platforms:', err));
    }
  }, [selectedLLM]);

  const modelColors = {
    'Gemma 2B': '#4ade80',
    'Gemma 7B': '#22c55e',
    'Llama3 8B': '#fbbf24',
    'CodeLlama 70B': '#fb923c',
    'Llama3 70B': '#ef4444',
  };

  useEffect(() => {
    if (co2Score !== null) {
      // Reset displayed score to 0 before starting animation
      setDisplayedScore(0);
      
      const duration = 2000;
      const steps = 60;
      const increment = co2Score / steps;
      let currentStep = 0;

      const timer = setInterval(() => {
        currentStep++;
        if (currentStep <= steps) {
          setDisplayedScore(prev => {
            const newValue = increment * currentStep;
            return newValue > co2Score ? co2Score : newValue;
          });
        } else {
          clearInterval(timer);
          setDisplayedScore(co2Score);
        }
      }, duration / steps);

      return () => clearInterval(timer);
    }
  }, [co2Score]);

  // Recalculate comparisons when co2Score or energyKwh changes
  const comparisons = useMemo(() => {
    return co2Score !== null ? getComparisons(co2Score) : null;
  }, [co2Score, energyKwh]);

  return (
    <div className="App">
      <div className="wave-decoration top-left-wave"></div>
      <div className="wave-decoration top-right-wave"></div>
      <div className="wave-decoration bottom-left-wave"></div>
      <div className="wave-decoration bottom-right-wave"></div>
      
      <div className="container">
        <div className="header-section">
          <div className="decorative-dots top-left">
            {[...Array(20)].map((_, i) => <span key={i} className="dot"></span>)}
          </div>
          <div className="decorative-dots top-right">
            {[...Array(20)].map((_, i) => <span key={i} className="dot"></span>)}
          </div>
          <div className="decorative-dots bottom-right">
            {[...Array(20)].map((_, i) => <span key={i} className="dot"></span>)}
          </div>
          <div className="leaf-decoration top-right-leaf">🍃</div>
          <div className="leaf-decoration bottom-right-leaf">🌿</div>
          <div className="leaf-decoration top-left-leaf">🍃</div>
          
          <h1 className="title">
            CO<sub>2</sub> Impact of LLM
          </h1>
        </div>
        
        <div className="selection-container">
          <div 
            className="dropdown-wrapper"
            onMouseLeave={() => handleMouseLeave('llm')}
          >
            <button 
              className="dropdown-button"
              onClick={() => setDropdownOpen({ ...dropdownOpen, llm: !dropdownOpen.llm })}
            >
              {selectedLLM || 'Select an LLM'}
              <span className="arrow">{dropdownOpen.llm ? '▲' : '▼'}</span>
            </button>
            {dropdownOpen.llm && (
              <div className="dropdown-menu">
                {(availableModels.length > 0 ? availableModels : llmOptions).map((llm) => (
                  <div 
                    key={llm}
                    className="dropdown-item"
                    onClick={() => handleLLMSelect(llm)}
                  >
                    {llm}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div 
            className="dropdown-wrapper"
            onMouseLeave={() => handleMouseLeave('platform')}
          >
            <button 
              className={`dropdown-button ${!selectedLLM ? 'disabled' : ''}`}
              onClick={() => selectedLLM && setDropdownOpen({ ...dropdownOpen, platform: !dropdownOpen.platform })}
              disabled={!selectedLLM}
            >
              {selectedPlatform || 'Select a platform'}
              <span className="arrow">{dropdownOpen.platform ? '▲' : '▼'}</span>
            </button>
            {dropdownOpen.platform && selectedLLM && (
              <div className="dropdown-menu">
                {availablePlatforms.map((platform) => (
                  <div 
                    key={platform}
                    className="dropdown-item"
                    onClick={() => handlePlatformSelect(platform)}
                  >
                    {platform}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div 
            className="dropdown-wrapper"
            onMouseLeave={() => handleMouseLeave('energy')}
          >
            <button 
              className={`dropdown-button ${!selectedPlatform ? 'disabled' : ''}`}
              onClick={() => selectedPlatform && setDropdownOpen({ ...dropdownOpen, energy: !dropdownOpen.energy })}
              disabled={!selectedPlatform}
            >
              {selectedEnergy ? energyOptions.find(e => e.value === selectedEnergy)?.name : 'Select energy source'}
              <span className="arrow">{dropdownOpen.energy ? '▲' : '▼'}</span>
            </button>
            {dropdownOpen.energy && selectedPlatform && (
              <div className="dropdown-menu">
                {energyOptions.map((energy) => (
                  <div 
                    key={energy.value}
                    className="dropdown-item"
                    onClick={() => handleEnergySelect(energy.value)}
                  >
                    {energy.name} ({energy.co2PerKwh} g/kWh)
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="prompt-wrapper">
            <input
              type="text"
              className={`prompt-input ${!selectedEnergy ? 'disabled' : ''}`}
              placeholder="Enter your prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!selectedEnergy}
            />
            <button 
              className={`submit-button ${!selectedEnergy || !prompt ? 'disabled' : ''}`}
              onClick={handleSubmit}
              disabled={!selectedEnergy || !prompt}
            >
              Submit
            </button>
          </div>
        </div>

        {co2Score === null && (
          <div className="charts-container">
            <div className="chart-card">
              <h3 className="chart-title">Energy Consumption by Model & Platform</h3>
              <div style={{ width: '100%', height: '180px' }}>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart 
                    data={energyByModelData} 
                    margin={{ top: 10, right: 10, left: 10, bottom: 30 }}
                    barCategoryGap="0%"
                    barGap={0}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#c8ddb5" />
                    <XAxis 
                      dataKey="platform"
                      tick={false}
                      axisLine={false}
                      height={1}
                    />
                    <YAxis 
                      tick={{ fontSize: 10 }} 
                      stroke="#5a7a4a" 
                      label={{ value: 'Wh', angle: -90, position: 'insideLeft', fontSize: 10 }}
                      domain={[0, 5]}
                      tickCount={6}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#f5f5f5', border: '1px solid #5a7a4a', borderRadius: '8px', fontSize: '11px' }}
                      formatter={(value, name, props) => [value.toFixed(3) + ' Wh', props.payload.platform]}
                      labelFormatter={(label, payload) => payload && payload[0] ? `${payload[0].payload.model}` : label}
                    />
                    <Bar 
                      dataKey="energy" 
                      radius={[4, 4, 0, 0]}
                      background={(props) => {
                        const { x, y, width, height, index } = props;
                        
                        // Déterminer le groupe du modèle pour l'arrière-plan
                        let modelIndex = 0;
                        let currentModel = null;
                        for (let i = 0; i <= index; i++) {
                          if (energyByModelData[i] && energyByModelData[i].model !== currentModel) {
                            if (i !== 0) modelIndex++;
                            currentModel = energyByModelData[i].model;
                          }
                        }
                        
                        // Couleur de fond selon le groupe (alternance blanc/gris plus foncé)
                        const bgColor = modelIndex % 2 === 0 ? '#e0e0e0' : '#ffffff';
                        
                        return (
                          <rect
                            x={x}
                            y={y}
                            width={width}
                            height={height}
                            fill={bgColor}
                          />
                        );
                      }}
                      shape={(props) => {
                        const { x, y, width, height, payload } = props;
                        
                        // Couleur de la barre selon la plateforme
                        let fill = '#8b5cf6'; // Violet pour Workstation
                        if (payload.platform === 'Server') fill = '#2563eb'; // Bleu
                        else if (payload.platform === 'Laptop') fill = '#10b981'; // Vert
                        
                        return (
                          <rect
                            x={x}
                            y={y}
                            width={width}
                            height={height}
                            fill={fill}
                            rx={4}
                            ry={4}
                          />
                        );
                      }}
                    />
                  </BarChart>
                </ResponsiveContainer>
                
                {/* Labels des modèles sous les groupes de barres */}
                <div style={{ 
                  position: 'relative',
                  height: '40px',
                  marginTop: '-15px',
                  marginLeft: '27px',
                  marginRight: '20px'
                }}>
                  {(() => {
                    const uniqueModels = [];
                    const modelIndices = []; // Position de la première barre de chaque modèle
                    const modelCounts = [];
                    let lastModel = null;
                    let count = 0;
                    let firstIndex = 0;
                    
                    energyByModelData.forEach((item, index) => {
                      if (item.model !== lastModel) {
                        if (lastModel !== null) {
                          uniqueModels.push(lastModel);
                          modelIndices.push(firstIndex);
                          modelCounts.push(count);
                        }
                        lastModel = item.model;
                        firstIndex = index;
                        count = 1;
                      } else {
                        count++;
                      }
                    });
                    
                    if (lastModel !== null) {
                      uniqueModels.push(lastModel);
                      modelIndices.push(firstIndex);
                      modelCounts.push(count);
                    }
                    
                    const totalBars = energyByModelData.length;
                    
                    return uniqueModels.map((model, idx) => {
                      // Centre du groupe de barres
                      const startPercent = (modelIndices[idx] / totalBars) * 100;
                      const widthPercent = (modelCounts[idx] / totalBars) * 100;
                      const centerPercent = startPercent + (widthPercent / 2);
                      
                      return (
                        <div 
                          key={model} 
                          style={{ 
                            position: 'absolute',
                            left: `${centerPercent}%`,
                            transform: 'translateX(-50%)',
                            fontSize: '9px',
                            color: '#5a7a4a',
                            fontWeight: '500',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          <span style={{
                            transform: 'rotate(-25deg)',
                            transformOrigin: 'center center',
                            display: 'inline-block'
                          }}>
                            {model}
                          </span>
                        </div>
                      );
                    });
                  })()}
                </div>
                
                {/* Légende des plateformes */}
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  gap: '15px',
                  marginTop: '-3px',
                  fontSize: '10px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#8b5cf6', borderRadius: '2px' }}></div>
                    <span style={{ color: '#5a7a4a' }}>Workstation</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#2563eb', borderRadius: '2px' }}></div>
                    <span style={{ color: '#5a7a4a' }}>Server</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '2px' }}></div>
                    <span style={{ color: '#5a7a4a' }}>Laptop</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="chart-card" style={{ minHeight: '250px', maxHeight: '280px', height: '280px' }}>
              <h3 className="chart-title">GPU vs CPU Energy Consumption by Model</h3>
              <div style={{ width: '100%', height: '215px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height={215}>
                  <BarChart data={gpuCpuDistributionData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#c8ddb5" />
                    <XAxis dataKey="model" tick={{ fontSize: 8 }} stroke="#5a7a4a" angle={-45} textAnchor="end" height={50} />
                    <YAxis tick={{ fontSize: 10 }} stroke="#5a7a4a" label={{ value: 'Wh', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#f5f5f5', border: '1px solid #5a7a4a', borderRadius: '8px', fontSize: '11px' }}
                      formatter={(value, name) => [`${value} Wh`, name]}
                    />
                    <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '0px', marginTop: '-15px' }} />
                    <Bar dataKey="GPU" fill="#8b5cf6" />
                    <Bar dataKey="CPU" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-card">
              <h3 className="chart-title">Energy Efficiency: Consumption vs Performance</h3>
              <div style={{ width: '100%', height: '215px' }}>
                <ResponsiveContainer width="100%" height={205}>
                  <LineChart 
                    data={(() => {
                      // Utiliser responseLength pour l'axe X
                      const allData = efficiencyData
                        .filter(d => d.model === 'Gemma 2B' || d.model === 'Gemma 7B')
                        .sort((a, b) => a.responseLength - b.responseLength);
                      
                      // Créer un objet par responseLength unique
                      const dataMap = {};
                      allData.forEach(d => {
                        const key = d.responseLength;
                        if (!dataMap[key]) {
                          dataMap[key] = { 
                            responseLength: key,
                            duration2B: null,
                            duration7B: null
                          };
                        }
                        if (d.model === 'Gemma 2B') {
                          dataMap[key]['Gemma 2B'] = d.energy;
                          dataMap[key].duration2B = d.duration;
                        } else if (d.model === 'Gemma 7B') {
                          dataMap[key]['Gemma 7B'] = d.energy;
                          dataMap[key].duration7B = d.duration;
                        }
                      });
                      
                      return Object.values(dataMap).sort((a, b) => a.responseLength - b.responseLength);
                    })()}
                    margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#c8ddb5" />
                    <XAxis 
                      dataKey="responseLength" 
                      tick={{ fontSize: 10 }} 
                      stroke="#5a7a4a" 
                      label={{ value: 'Response Length (words)', position: 'insideBottom', offset: -5, fontSize: 10 }}
                    />
                    <YAxis 
                      tick={{ fontSize: 10 }} 
                      stroke="#5a7a4a" 
                      label={{ value: 'Wh', angle: -90, position: 'insideLeft', fontSize: 10 }}
                      domain={[0, 'auto']}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#f5f5f5', border: '1px solid #5a7a4a', borderRadius: '8px', fontSize: '11px' }}
                      formatter={(value, name, props) => {
                        if (!value) return ['-'];
                        const duration = name === 'Gemma 2B' ? props.payload.duration2B : props.payload.duration7B;
                        return [`${value.toFixed(4)} Wh${duration ? ` (${duration}s)` : ''}`];
                      }}
                      labelFormatter={(value) => `${value} words`}
                    />
                    <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '5px' }} />
                    <Line name="Gemma 2B" type="monotone" dataKey="Gemma 2B" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 3 }} connectNulls />
                    <Line name="Gemma 7B" type="monotone" dataKey="Gemma 7B" stroke="#8b5cf6" strokeWidth={2} dot={{ fill: '#8b5cf6', r: 3 }} connectNulls />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {co2Score !== null && (
          <div className="co2-container">
            <button className="close-button" onClick={handleCloseResults}>✕</button>
            <h2 className="co2-title">CO2 Consumption</h2>
            <div className="co2-score-display">
              <div className="co2-value">
                <span className="co2-number">
                  {displayedScore < 10 
                    ? displayedScore.toFixed(3) 
                    : displayedScore.toFixed(2)}
                </span>
                <span className="co2-unit">mg CO₂</span>
              </div>
            </div>
            
            <div className="comparisons-grid">
              <div className="comparison-card">
                <div className="comparison-icon">📱</div>
                <div className="comparison-content">
                  <div className="comparison-value">{comparisons.smartphones}%</div>
                  <div className="comparison-label">of a smartphone charge</div>
                  <div className="comparison-source">Source: Next Business Energy</div>
                </div>
              </div>
              
              <div className="comparison-card">
                <div className="comparison-icon">💡</div>
                <div className="comparison-content">
                  <div className="comparison-value">{comparisons.ledHours} min</div>
                  <div className="comparison-label">of LED lighting</div>
                  <div className="comparison-source">Source: Solar Technologies</div>
                </div>
              </div>
              
              <div className="comparison-card">
                <div className="comparison-icon">🌳</div>
                <div className="comparison-content">
                  <div className="comparison-value">{comparisons.treeDays}s</div>
                  <div className="comparison-label">of tree absorption</div>
                  <div className="comparison-source">Source: ForTomorrow, Viessmann</div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="footer-decorations">
          <div className="tree-left">🌳</div>
          <div className="tree-left-small">🌲</div>
          <div className="tree-center">🌳</div>
          <div className="grass-left">🌿</div>
          <div className="grass-right">🌿</div>
          <div className="leaves-falling">
            <span className="falling-leaf">🍃</span>
            <span className="falling-leaf">🍃</span>
            <span className="falling-leaf">🍂</span>
            <span className="falling-leaf">🍃</span>
            <span className="falling-leaf" style={{ left: '15%', animationDelay: '1s', animationDuration: '4s' }}>🍂</span>
            <span className="falling-leaf" style={{ left: '25%', animationDelay: '2s', animationDuration: '5s' }}>🍃</span>
            <span className="falling-leaf" style={{ left: '35%', animationDelay: '0.5s', animationDuration: '6s' }}>🍂</span>
            <span className="falling-leaf" style={{ left: '45%', animationDelay: '1.5s', animationDuration: '5.5s' }}>🍃</span>
            <span className="falling-leaf" style={{ left: '55%', animationDelay: '0.8s', animationDuration: '4.5s' }}>🍂</span>
            <span className="falling-leaf" style={{ left: '65%', animationDelay: '2.5s', animationDuration: '5s' }}>🍃</span>
            <span className="falling-leaf" style={{ left: '75%', animationDelay: '1.2s', animationDuration: '6s' }}>🍂</span>
            <span className="falling-leaf" style={{ left: '85%', animationDelay: '3s', animationDuration: '4.8s' }}>🍃</span>
            <span className="falling-leaf" style={{ left: '20%', animationDelay: '3.5s', animationDuration: '5.2s' }}>🍃</span>
            <span className="falling-leaf" style={{ left: '60%', animationDelay: '2.2s', animationDuration: '4.3s' }}>🍂</span>
            <span className="falling-leaf" style={{ left: '40%', animationDelay: '1.8s', animationDuration: '5.7s' }}>🍃</span>
            <span className="falling-leaf" style={{ left: '70%', animationDelay: '0.3s', animationDuration: '4.9s' }}>🍂</span>
          </div>
          {/* Forêt dense - 16 arbres répartis sur toute la largeur */}
          <div style={{ position: 'absolute', bottom: '5px', left: '5%', fontSize: '33px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '12%', fontSize: '30px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '18%', fontSize: '35px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '24%', fontSize: '32px' }}>🌴</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '30%', fontSize: '34px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '36%', fontSize: '31px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '42%', fontSize: '33px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '48%', fontSize: '30px' }}>🌴</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '54%', fontSize: '35px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '60%', fontSize: '32px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '66%', fontSize: '34px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '72%', fontSize: '31px' }}>🌴</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '78%', fontSize: '33px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '84%', fontSize: '32px' }}>🌲</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '90%', fontSize: '30px' }}>🌳</div>
          <div style={{ position: 'absolute', bottom: '5px', left: '95%', fontSize: '34px' }}>🌲</div>
        </div>
      </div>
    </div>
  );
}

export default App;
