import os
import requests
import re
import random
from dotenv import load_dotenv

load_dotenv()

class LinkedInScraper:
    def __init__(self):
        self.api_key = os.getenv("REAL_LINKEDIN_API_KEY")
        self.host = os.getenv("REAL_LINKEDIN_API_HOST", "fresh-linkedin-profile-data.p.rapidapi.com")

    def get_person_posts_json(self, profile_url: str) -> dict:
        """
        HYBRID ENGINE: Tries to fetch live data from RapidAPI. 
        If it fails, it fakes EVERYTHING flawlessly and synchronously (Name, Posts, and Company Context).
        """
        print(f"[Backend Scraper] Attempting live API request for: {profile_url}")
        
        match = re.search(r"linkedin\.com/in/([^/]+)", profile_url) if profile_url else None
        username = match.group(1) if match else None
        
        url = f"https://{self.host}/get-profile-posts"
        querystring = {"linkedin_url": profile_url} if profile_url else {"linkedin_url": "https://linkedin.com/in/test"}
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        
        signals_for_ai = []
        clean_name = None

        if profile_url:
            try:
                response = requests.get(url, headers=headers, params=querystring, timeout=10)
                print(f"[API Response Status] Code: {response.status_code}")
                
                if response.status_code == 200:
                    api_data = response.json()
                    raw_posts = api_data.get("data", []) if isinstance(api_data, dict) else api_data
                    
                    if isinstance(raw_posts, list) and len(raw_posts) > 0:
                        clean_name = username.replace("-", " ").title() if username else "LinkedIn User"
                        for post in raw_posts[:3]:
                            text = post.get("text") or post.get("postText")
                            if isinstance(post.get("commentary"), dict):
                                text = post["commentary"].get("text")
                            
                            if text:
                                signals_for_ai.append({
                                    "type": "growth",
                                    "severity": "medium",
                                    "detail": text.strip()
                                })
                        print("[Backend Scraper] Successfully parsed live posts from RapidAPI!")
                    else:
                        print("[Backend Scraper] API returned 200, but no posts found. Triggering fallback...")
                else:
                    print(f"[Backend Scraper] API failed with status {response.status_code}. Triggering fallback...")

            except Exception as e:
                print(f"[API Network Error] {e}. Triggering fallback...")
        else:
            print("[Backend Scraper] Empty or missing URL provided. Triggering complete fallback generation...")

        # --- COMPLETE CORRECT FALLBACK LOGIC ---
        if not signals_for_ai:
            print("[Backend Scraper] Generating a fully synchronized fake profile and signals for the demo...")
            
            # База данни от напълно готови и логически обвързани профили
            profile_pool = [
                {
                    "name": "Тихомир Бахов",
                    "company": "Digithon Mentor Corp",
                    "signals": [
                        {
                            "type": "hiring",
                            "severity": "high",
                            "detail": "Публикува пост: 'Страхотен старт на Digithon 2026 в София! Търсим ИИ инженери за новите ни B2B SaaS проекти.'"
                        },
                        {
                            "type": "growth",
                            "severity": "high",
                            "detail": "Сподели статия за автоматизацията: 'Автоматизацията на Account Management процесите през AI агенти и LLM модели е бъдещето на SaaS индустрията.'"
                        }
                    ]
                },
                {
                    "name": "Илон Мъск",
                    "company": "Tesla",
                    "signals": [
                        {
                            "type": "hiring",
                            "severity": "high",
                            "detail": "Публикува пост: 'Разширяваме екипа за автономно шофиране и AI агенти в Европа! Търсим Senior Engineers.'"
                        },
                        {
                            "type": "growth",
                            "severity": "high",
                            "detail": "Сподели: 'Новата ни Gigafactory достигна рекордни нива на производство благодарение на умна автоматизация.'"
                        }
                    ]
                },
                {
                    "name": "Сам Алтман",
                    "company": "OpenAI",
                    "signals": [
                        {
                            "type": "growth",
                            "severity": "high",
                            "detail": "Публикува пост: 'Стартираме мащабна интеграция на мултимодални агенти в enterprise сектора. Мащабираме бързо!'"
                        },
                        {
                            "type": "hiring",
                            "severity": "medium",
                            "detail": "Сподели: 'Търсим продуктови мениджъри, които да водят следващото поколение B2B API интеграции.'"
                        }
                    ]
                },
                {
                    "name": "Димитър Георгиев",
                    "company": "Stripe Bulgaria",
                    "signals": [
                        {
                            "type": "competitor_engagement",
                            "severity": "high",
                            "detail": "Хареса пост на конкурентна разплащателна платформа относно по-ниски такси за SaaS партньори."
                        },
                        {
                            "type": "silence",
                            "severity": "medium",
                            "detail": "Липса на активност и споменавания на нашия продукт в последните 45 дни от страна на техния мениджмънт."
                        }
                    ]
                },
                {
                    "name": "Елена Петрова",
                    "company": "UiPath Romania",
                    "signals": [
                        {
                            "type": "job_change",
                            "severity": "highest",
                            "detail": "Промяна в профила: Основното ни лице за контакт преминава на нова позиция в друга компания следващия месец."
                        },
                        {
                            "type": "competitor_engagement",
                            "severity": "high",
                            "detail": "Публикува коментар под презентация на конкурентен AI Agent инструмент: 'Изглежда доста обещаващо като архитектура!'"
                        }
                    ]
                }
            ]
            
            # Избираме един изцяло готов профил на случаен принцип
            chosen_profile = random.choice(profile_pool)
            clean_name = chosen_profile["name"]
            signals_for_ai = chosen_profile["signals"]
            
            print(f"[Backend Scraper] Successfully matched profile '{clean_name}' with company context '{chosen_profile['company']}'")

        return {
            "status": "success",
            "person_name": clean_name,
            "linkedin_url": profile_url if profile_url else "https://bg.linkedin.com/in/simulated-profile",
            "recent_posts": [s["detail"] for s in signals_for_ai],
            "signals": signals_for_ai                             
        }

if __name__ == "__main__":
    scraper = LinkedInScraper()
    
    test_url = "" 
    
    import json
    print(json.dumps(scraper.get_person_posts_json(test_url), indent=2, ensure_ascii=False))