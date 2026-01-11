
import requests

def get_wordpress_posts(site_url, per_page=10):
    endpoint = site_url.rstrip('/') + '/wp-json/wp/v2/posts'
    params = {'per_page': per_page, 'status': 'publish'}
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        posts = response.json()
        simplified = []
        for post in posts:
            simplified.append({
                'title': post['title']['rendered'],
                'slug': post['slug'],
                'date': post['date']
            })
        return simplified, None
    except Exception as e:
        return None, str(e)
