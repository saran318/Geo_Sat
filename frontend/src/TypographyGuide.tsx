import React, { useEffect } from 'react';

const FONT_LINKS = [
  'https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Geist+Mono:wght@100..900&family=Inter:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&family=Chakra+Petch:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700&family=Fraunces:wght@400;500;600;700&family=Instrument+Serif&family=Barlow+Condensed:wght@400;500;600;700&family=Big+Shoulders+Display:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap',
  'https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&f[]=satoshi@400,500,600,700&display=swap',
  'https://cdn.jsdelivr.net/npm/commit-mono@1.136/css/commitmono.css'
];

const FONTS_CSS = `
/* Clean / Neutral */
.font-geist { font-family: 'Geist', sans-serif !important; }
.font-inter { font-family: 'Inter', sans-serif !important; }
.font-public { font-family: 'Public Sans', sans-serif !important; }
.font-general { font-family: 'General Sans', sans-serif !important; }

/* Geometric / Modern Tech */
.font-space-grotesk { font-family: 'Space Grotesk', sans-serif !important; }
.font-satoshi { font-family: 'Satoshi', sans-serif !important; }
.font-manrope { font-family: 'Manrope', sans-serif !important; }

/* Technical / Sci-Fi */
.font-chakra { font-family: 'Chakra Petch', sans-serif !important; }
.font-rajdhani { font-family: 'Rajdhani', sans-serif !important; }
.font-orbitron { font-family: 'Orbitron', sans-serif !important; }

/* Editorial / Premium Serif */
.font-fraunces { font-family: 'Fraunces', serif !important; }
.font-instrument { font-family: 'Instrument Serif', serif !important; }

/* Condensed */
.font-barlow { font-family: 'Barlow Condensed', sans-serif !important; }
.font-big-shoulders { font-family: 'Big Shoulders Display', sans-serif !important; }

/* Monospace */
.font-geist-mono { font-family: 'Geist Mono', monospace !important; }
.font-jetbrains { font-family: 'JetBrains Mono', monospace !important; }
.font-space-mono { font-family: 'Space Mono', monospace !important; }
.font-commit-mono { font-family: 'CommitMono', 'Commit Mono', monospace !important; }
`;

const CATEGORIES = [
  {
    title: 'Clean / Neutral Sans',
    fonts: [
      { id: 'geist', name: 'Geist Sans', class: 'font-geist', showBody: true },
      { id: 'inter', name: 'Inter', class: 'font-inter', showBody: true },
      { id: 'public', name: 'Public Sans', class: 'font-public', showBody: true },
      { id: 'general', name: 'General Sans (Neue Montreal alt)', class: 'font-general', showBody: true },
    ],
  },
  {
    title: 'Geometric / Modern Tech',
    fonts: [
      { id: 'space-grotesk', name: 'Space Grotesk', class: 'font-space-grotesk', showBody: true },
      { id: 'satoshi', name: 'Satoshi', class: 'font-satoshi', showBody: true },
      { id: 'manrope', name: 'Manrope', class: 'font-manrope', showBody: true },
    ],
  },
  {
    title: 'Technical / Sci-Fi / Instrument-Panel (Headings Only)',
    fonts: [
      { id: 'chakra', name: 'Chakra Petch', class: 'font-chakra', showBody: false },
      { id: 'rajdhani', name: 'Rajdhani', class: 'font-rajdhani', showBody: false },
      { id: 'orbitron', name: 'Orbitron', class: 'font-orbitron', showBody: false },
    ],
  },
  {
    title: 'Editorial / Premium Serif (Hero Headings Only)',
    fonts: [
      { id: 'fraunces', name: 'Fraunces', class: 'font-fraunces', showBody: false },
      { id: 'instrument', name: 'Instrument Serif', class: 'font-instrument', showBody: false },
    ],
  },
  {
    title: 'Condensed (Tight Labels / Badges)',
    fonts: [
      { id: 'barlow', name: 'Barlow Condensed', class: 'font-barlow', showBody: true },
      { id: 'big-shoulders', name: 'Big Shoulders Display', class: 'font-big-shoulders', showBody: true },
    ],
  },
];

const MONO_FONTS = [
  { id: 'geist-mono', name: 'Geist Mono', class: 'font-geist-mono' },
  { id: 'jetbrains', name: 'JetBrains Mono', class: 'font-jetbrains' },
  { id: 'space-mono', name: 'Space Mono', class: 'font-space-mono' },
  { id: 'commit', name: 'Commit Mono', class: 'font-commit-mono' },
];

export const TypographyGuide = () => {
  useEffect(() => {
    const links = FONT_LINKS.map((url) => {
      const link = document.createElement('link');
      link.href = url;
      link.rel = 'stylesheet';
      document.head.appendChild(link);
      return link;
    });

    return () => {
      links.forEach((link) => {
        if (link.parentNode) {
          link.parentNode.removeChild(link);
        }
      });
    };
  }, []);

  return (
    <div style={{ backgroundColor: '#f9fafb', color: '#111827', minHeight: '100vh', padding: '60px 40px', fontFamily: 'sans-serif' }}>
      <style dangerouslySetInnerHTML={{ __html: FONTS_CSS }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ marginBottom: '80px', paddingBottom: '20px', borderBottom: '1px solid #e5e7eb' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', margin: 0, letterSpacing: '-0.02em' }}>Typography Style Guide</h1>
          <p style={{ fontSize: '15px', color: '#6b7280', marginTop: '12px', maxWidth: '600px', lineHeight: '1.5' }}>
            Standalone route for evaluating typefaces. Grouped by category and paired at the bottom.
            Zero impact on the production app.
          </p>
        </header>

        {CATEGORIES.map((category, idx) => (
          <section key={idx} style={{ marginBottom: '100px' }}>
            <h2 style={{ fontSize: '14px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#4b5563', marginBottom: '32px', borderLeft: '4px solid #d1d5db', paddingLeft: '16px' }}>
              {category.title}
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '60px' }}>
              {category.fonts.map((font) => (
                <div key={font.id} className={font.class} style={{ backgroundColor: '#ffffff', padding: '48px', borderRadius: '16px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                  {/* Font Label */}
                  <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.12em', color: '#9ca3af', marginBottom: '24px', fontWeight: '600', fontFamily: 'sans-serif' }}>
                    {font.name}
                  </div>

                  {/* Small-caps/tracked label */}
                  <div style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: '600', color: '#4b5563', marginBottom: '16px' }}>
                    GEOSAT INTELLIGENCE ENGINE
                  </div>

                  {/* Large Heading */}
                  <h3 style={{ fontSize: '40px', fontWeight: '700', lineHeight: '1.1', margin: '0 0 24px 0', color: '#111827' }}>
                    Satellite Land-Use & Change Detection
                  </h3>

                  {/* Body Paragraph */}
                  {font.showBody && (
                    <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#374151', maxWidth: '750px', margin: '0 0 40px 0', fontWeight: '400' }}>
                      Evaluating multi-temporal spectral shifts across 85.59 km² of the Bengaluru metropolitan region using 6-channel Sentinel-2 tensor extraction and ResNet-50 classification. This robust methodology allows for accurate tracking of urban sprawl and surface water reduction over five years.
                    </p>
                  )}

                  {/* Weight Samples */}
                  <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap', borderTop: '1px solid #f3f4f6', paddingTop: '32px', marginTop: !font.showBody ? '40px' : '0' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'sans-serif' }}>Regular (400)</span>
                      <span style={{ fontSize: '18px', fontWeight: '400', color: '#111827' }}>The quick brown fox.</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'sans-serif' }}>Medium (500)</span>
                      <span style={{ fontSize: '18px', fontWeight: '500', color: '#111827' }}>The quick brown fox.</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'sans-serif' }}>Semibold (600)</span>
                      <span style={{ fontSize: '18px', fontWeight: '600', color: '#111827' }}>The quick brown fox.</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'sans-serif' }}>Bold (700)</span>
                      <span style={{ fontSize: '18px', fontWeight: '700', color: '#111827' }}>The quick brown fox.</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}

        {/* Monospace Section */}
        <section style={{ marginBottom: '120px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#4b5563', marginBottom: '32px', borderLeft: '4px solid #d1d5db', paddingLeft: '16px' }}>
            Monospace (Data & Numerics)
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '60px' }}>
            {MONO_FONTS.map((font) => (
              <div key={font.id} className={font.class} style={{ backgroundColor: '#ffffff', padding: '48px', borderRadius: '16px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                {/* Font Label */}
                <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.12em', color: '#9ca3af', marginBottom: '32px', fontWeight: '600', fontFamily: 'sans-serif' }}>
                  {font.name}
                </div>

                {/* Numeric / Stat Sample */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '40px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '400' }}>
                    Small size (12-14px)
                  </div>
                  <div style={{ fontSize: '14px', color: '#374151', fontWeight: '500', padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px', border: '1px solid #f3f4f6' }}>
                    37.5 km² · 42.15 km² · Split: 50% / 50%<br />
                    Extent: 12.97°N, 77.59°E · 10m Ground Resolution
                  </div>

                  <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '400', marginTop: '16px' }}>
                    Large size (24-32px)
                  </div>
                  <div style={{ fontSize: '32px', color: '#111827', fontWeight: '700' }}>
                    +10.75 km² (34.2%)
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>


        {/* Pairings Section */}
        <section style={{ paddingBottom: '100px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '700', letterSpacing: '-0.02em', color: '#111827', marginBottom: '40px', borderBottom: '2px solid #e5e7eb', paddingBottom: '16px' }}>
            Holistic Pairings (In-Context)
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '80px' }}>
            
            {/* Pairing A */}
            <div style={{ backgroundColor: '#ffffff', padding: '48px', borderRadius: '16px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#9ca3af', marginBottom: '32px', fontWeight: '600', fontFamily: 'sans-serif' }}>
                Pairing A: Space Grotesk (H) + Inter (Body) + Space Mono (Data)
              </div>
              <div style={{ maxWidth: '800px' }}>
                <div className="font-inter" style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: '600', color: '#4b5563', marginBottom: '16px' }}>
                  GEOSAT INTELLIGENCE ENGINE
                </div>
                <h3 className="font-space-grotesk" style={{ fontSize: '40px', fontWeight: '700', lineHeight: '1.1', margin: '0 0 24px 0', color: '#111827' }}>
                  Satellite Land-Use & Change Detection
                </h3>
                <p className="font-inter" style={{ fontSize: '15px', lineHeight: '1.6', color: '#374151', margin: '0 0 32px 0', fontWeight: '400' }}>
                  Evaluating multi-temporal spectral shifts across 85.59 km² of the Bengaluru metropolitan region using 6-channel Sentinel-2 tensor extraction and ResNet-50 classification. This robust methodology allows for accurate tracking of urban sprawl and surface water reduction over five years.
                </p>
                <div className="font-space-mono" style={{ padding: '24px', backgroundColor: '#f3f4f6', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>Built-Up Expansion</div>
                    <div style={{ fontSize: '28px', color: '#111827', fontWeight: '700' }}>+10.75 km²</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>Confidence</div>
                    <div style={{ fontSize: '28px', color: '#10b981', fontWeight: '700' }}>94.2%</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Pairing B */}
            <div style={{ backgroundColor: '#ffffff', padding: '48px', borderRadius: '16px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#9ca3af', marginBottom: '32px', fontWeight: '600', fontFamily: 'sans-serif' }}>
                Pairing B: Chakra Petch (H) + Public Sans (Body) + JetBrains Mono (Data)
              </div>
              <div style={{ maxWidth: '800px' }}>
                <div className="font-public" style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: '600', color: '#4b5563', marginBottom: '16px' }}>
                  GEOSAT INTELLIGENCE ENGINE
                </div>
                <h3 className="font-chakra" style={{ fontSize: '40px', fontWeight: '700', lineHeight: '1.1', margin: '0 0 24px 0', color: '#111827' }}>
                  Satellite Land-Use & Change Detection
                </h3>
                <p className="font-public" style={{ fontSize: '15px', lineHeight: '1.6', color: '#374151', margin: '0 0 32px 0', fontWeight: '400' }}>
                  Evaluating multi-temporal spectral shifts across 85.59 km² of the Bengaluru metropolitan region using 6-channel Sentinel-2 tensor extraction and ResNet-50 classification. This robust methodology allows for accurate tracking of urban sprawl and surface water reduction over five years.
                </p>
                <div className="font-jetbrains" style={{ padding: '24px', backgroundColor: '#f3f4f6', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>Built-Up Expansion</div>
                    <div style={{ fontSize: '28px', color: '#111827', fontWeight: '700' }}>+10.75 km²</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>Confidence</div>
                    <div style={{ fontSize: '28px', color: '#10b981', fontWeight: '700' }}>94.2%</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Pairing C */}
            <div style={{ backgroundColor: '#ffffff', padding: '48px', borderRadius: '16px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#9ca3af', marginBottom: '32px', fontWeight: '600', fontFamily: 'sans-serif' }}>
                Pairing C: Fraunces (Hero) + General Sans (Body) + Commit Mono (Data)
              </div>
              <div style={{ maxWidth: '800px' }}>
                <div className="font-general" style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: '600', color: '#4b5563', marginBottom: '16px' }}>
                  GEOSAT INTELLIGENCE ENGINE
                </div>
                <h3 className="font-fraunces" style={{ fontSize: '40px', fontWeight: '500', lineHeight: '1.1', margin: '0 0 24px 0', color: '#111827' }}>
                  Satellite Land-Use & Change Detection
                </h3>
                <p className="font-general" style={{ fontSize: '15px', lineHeight: '1.6', color: '#374151', margin: '0 0 32px 0', fontWeight: '400' }}>
                  Evaluating multi-temporal spectral shifts across 85.59 km² of the Bengaluru metropolitan region using 6-channel Sentinel-2 tensor extraction and ResNet-50 classification. This robust methodology allows for accurate tracking of urban sprawl and surface water reduction over five years.
                </p>
                <div className="font-commit-mono" style={{ padding: '24px', backgroundColor: '#f3f4f6', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>Built-Up Expansion</div>
                    <div style={{ fontSize: '28px', color: '#111827', fontWeight: '600' }}>+10.75 km²</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', textTransform: 'uppercase' }}>Confidence</div>
                    <div style={{ fontSize: '28px', color: '#10b981', fontWeight: '600' }}>94.2%</div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </section>

      </div>
    </div>
  );
};
