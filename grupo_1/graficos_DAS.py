import seaborn as sns

# Visualización de la evolución temporal de la capacidad instalada, disponible y no disponible
plt.figure(figsize=(10, 6))
plt.plot(df['Publication date'], df['Installed capacity'], label='Installed capacity')
plt.plot(df['Publication date'], df['Available capacity'], label='Available capacity')
plt.plot(df['Publication date'], df['Unavailable capacity'], label='Unavailable capacity')
plt.xlabel('Date')
plt.ylabel('Capacity')
plt.title('Evolution of Capacity Over Time')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gráfico de barras para comparar la capacidad instalada por tipo de combustible
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='Fuel type', y='Installed capacity', estimator=sum)
plt.xlabel('Fuel Type')
plt.ylabel('Installed Capacity')
plt.title('Installed Capacity by Fuel Type')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Análisis de correlación entre las diferentes capacidades
correlation_matrix = df[['Installed capacity', 'Available capacity', 'Unavailable capacity']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()

# Identificación de insights
# Por ejemplo, podríamos explorar si hay una correlación entre la capacidad instalada y la disponible
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Installed capacity', y='Available capacity')
plt.xlabel('Installed Capacity')
plt.ylabel('Available Capacity')
plt.title('Installed vs Available Capacity')
plt.tight_layout()
plt.show()fd